"""
OSSIA experimental segmentation:
- estimates a broad carpal-bone envelope,
- separates connected candidate bone regions with distance-transform watershed,
- estimates radiopaque/ossification candidates inside each instance,
- reports per-instance and total area ratios.

This is an exploratory classical-CV baseline, not validated anatomical segmentation.
The numbered instances are NOT guaranteed to correspond to named carpal bones.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
import csv
import cv2
import numpy as np


def _gray(image: np.ndarray) -> np.ndarray:
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Citra kosong/tidak valid.")
    if image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if image.ndim != 2:
        raise ValueError("Input harus berupa citra grayscale atau BGR.")
    if image.dtype != np.uint8:
        image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return image


def _largest_components(mask: np.ndarray, min_area: int, max_components: int = 8):
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    comps = []
    for i in range(1, n):
        area = int(stats[i, cv2.CC_STAT_AREA])
        if area >= min_area:
            comps.append((area, i))
    comps.sort(reverse=True)
    out = np.zeros_like(mask)
    for _, i in comps[:max_components]:
        out[labels == i] = 255
    return out


def _watershed_instances(bone_mask: np.ndarray, min_seed_distance: int = 22,
                         min_area: int = 500, max_instances: int = 8):
    """Split merged foreground blobs using distance-transform local maxima."""
    binary = (bone_mask > 0).astype(np.uint8)
    if not np.any(binary):
        return np.zeros_like(bone_mask, dtype=np.int32)

    dist = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
    # Local maxima become markers. A relative threshold suppresses tiny peaks.
    peak_floor = max(3.0, float(dist.max()) * 0.22)
    dil_k = max(3, min_seed_distance // 2 * 2 + 1)
    local_max = (dist >= cv2.dilate(dist, np.ones((dil_k, dil_k), np.uint8)) - 1e-4)
    peaks = (local_max & (dist >= peak_floor) & (binary > 0)).astype(np.uint8) * 255

    n, peak_labels, peak_stats, peak_centroids = cv2.connectedComponentsWithStats(peaks, 8)
    peak_list = []
    for i in range(1, n):
        x, y = peak_centroids[i]
        peak_list.append((float(dist[int(round(y)), int(round(x))]), int(x), int(y)))
    peak_list.sort(reverse=True)
    peak_list = peak_list[:max_instances]

    markers = np.zeros(binary.shape, dtype=np.int32)
    for idx, (_, x, y) in enumerate(peak_list, start=2):
        cv2.circle(markers, (x, y), 2, int(idx), -1)

    if not peak_list:
        # Fall back to connected components if no reliable distance peaks exist.
        count, cc = cv2.connectedComponents(binary, 8)
        return cc.astype(np.int32)

    # Watershed requires a 3-channel image. Use inverse distance as topography.
    norm = cv2.normalize(dist, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    topo = cv2.cvtColor(255 - norm, cv2.COLOR_GRAY2BGR)
    markers[binary == 0] = 1
    cv2.watershed(topo, markers)

    # Keep watershed labels inside the bone foreground and filter tiny basins.
    result = np.zeros(binary.shape, dtype=np.int32)
    areas = []
    for lab in np.unique(markers):
        if lab <= 1:
            continue
        area = int(np.count_nonzero((markers == lab) & (binary > 0)))
        if area >= min_area:
            areas.append((area, int(lab)))
    areas.sort(reverse=True)
    for new_id, (_, old_id) in enumerate(areas[:max_instances], start=1):
        result[(markers == old_id) & (binary > 0)] = new_id
    return result


def segment_carpal_bones_and_ossification(
    image: np.ndarray,
    *,
    roi_top_fraction: float = 0.01,
    roi_bottom_fraction: float = 0.86,
    bone_percentile: float = 42.0,
    ossification_percentile: float = 72.0,
    close_kernel: int = 11,
    min_bone_area: int = 500,
    min_instance_area: int = 500,
    min_seed_distance: int = 22,
    max_instances: int = 8,
) -> dict[str, Any]:
    gray = _gray(image)
    h, w = gray.shape
    if not (0 < roi_top_fraction < roi_bottom_fraction <= 1):
        raise ValueError("Batas ROI vertikal tidak valid.")
    if not (0 < bone_percentile < 100 and 0 < ossification_percentile < 100):
        raise ValueError("Percentile harus antara 0 dan 100.")
    if close_kernel < 3 or close_kernel % 2 == 0:
        raise ValueError("close_kernel harus ganjil dan minimal 3.")

    # Contrast normalization; bilateral filtering preserves edges better than
    # a strong Gaussian blur for this exploratory pipeline.
    denoised = cv2.bilateralFilter(gray, 7, 35, 35)
    enhanced = cv2.createCLAHE(clipLimit=1.7, tileGridSize=(8, 8)).apply(denoised)

    # The supplied ROI includes a small part of distal radius/ulna at its bottom.
    # Limit the analysis window; users can adjust this fraction per ROI.
    y0 = int(round(h * roi_top_fraction))
    y1 = int(round(h * roi_bottom_fraction))
    analysis = np.zeros((h, w), np.uint8)
    analysis[y0:y1, :] = 255

    vals = enhanced[analysis > 0]
    bone_thr = float(np.percentile(vals, bone_percentile))
    raw_bone = ((enhanced >= bone_thr) & (analysis > 0)).astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_kernel, close_kernel))
    bone_mask = cv2.morphologyEx(raw_bone, cv2.MORPH_CLOSE, k, iterations=2)
    bone_mask = cv2.morphologyEx(
        bone_mask, cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1
    )
    bone_mask = _largest_components(bone_mask, min_bone_area, max_components=16)
    bone_mask[analysis == 0] = 0

    labels = _watershed_instances(
        bone_mask, min_seed_distance=min_seed_distance,
        min_area=min_instance_area, max_instances=max_instances
    )

    # Candidate radiopaque pixels are estimated separately within each instance.
    candidate_mask = np.zeros_like(gray, np.uint8)
    per_bone = []
    for lab in sorted(int(v) for v in np.unique(labels) if v > 0):
        region = (labels == lab)
        pix = enhanced[region]
        if pix.size == 0:
            continue
        thr = float(np.percentile(pix, ossification_percentile))
        cand = region & (enhanced >= thr)
        # Remove isolated one-pixel speckles without filling trabecular spaces.
        cand_u8 = cand.astype(np.uint8) * 255
        cand_u8 = cv2.morphologyEx(
            cand_u8, cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1
        )
        candidate_mask[cand_u8 > 0] = 255
        bone_area = int(region.sum())
        oss_area = int(np.count_nonzero(cand_u8))
        per_bone.append({
            "instance_id": lab,
            "bone_area_px": bone_area,
            "candidate_ossification_area_px": oss_area,
            "candidate_ratio_percent": round(100.0 * oss_area / bone_area, 3) if bone_area else 0.0,
            "intensity_threshold": round(thr, 2),
        })

    total_bone = int(np.count_nonzero(labels))
    total_oss = int(np.count_nonzero(candidate_mask))
    total_ratio = 100.0 * total_oss / total_bone if total_bone else 0.0

    # Color labels and candidate overlay.
    palette = [
        (255, 120, 50), (50, 200, 255), (120, 255, 80), (220, 80, 220),
        (50, 220, 180), (180, 180, 50), (80, 120, 255), (200, 100, 100)
    ]
    instance_overlay = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    label_color = np.zeros_like(instance_overlay)
    for row in per_bone:
        lab = row["instance_id"]
        label_color[labels == lab] = palette[(lab - 1) % len(palette)]
    instance_overlay = cv2.addWeighted(instance_overlay, 0.58, label_color, 0.42, 0)

    oss_overlay = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    red = oss_overlay.copy()
    red[candidate_mask > 0] = (0, 0, 255)
    oss_overlay = cv2.addWeighted(oss_overlay, 0.65, red, 0.35, 0)

    # Total mask is the union of all instance labels.
    total_bone_mask = (labels > 0).astype(np.uint8) * 255
    warnings = [
        "Instance 1..N adalah label hasil pemisahan algoritmik, bukan nama tulang karpal anatomis.",
        "Kandidat osifikasi berbasis intensitas radiograf; bukan segmentasi pusat osifikasi tervalidasi.",
        "Nilai rasio adalah rasio kandidat piksel terhadap mask tulang hasil algoritma, bukan rasio klinis.",
        "Perlu anotasi ahli/ground truth dan evaluasi Dice-IoU sebelum klaim akurasi atau penggunaan klinis."
    ]
    if len(per_bone) < 8:
        warnings.append(f"Hanya {len(per_bone)} instance terdeteksi; tidak berarti seluruh tulang karpal sudah tersegmentasi.")
    if len(per_bone) > 8:
        warnings.append("Jumlah instance melebihi delapan; beberapa tulang mungkin terpecah atau struktur lain ikut terdeteksi.")

    return {
        "enhanced_image": enhanced,
        "analysis_window_mask": analysis,
        "bone_mask": total_bone_mask,
        "instance_labels": labels,
        "instance_overlay": instance_overlay,
        "ossification_candidate_mask": candidate_mask,
        "ossification_overlay": oss_overlay,
        "per_bone": per_bone,
        "summary": {
            "detected_instances": len(per_bone),
            "total_bone_area_px": total_bone,
            "total_candidate_ossification_area_px": total_oss,
            "total_candidate_ratio_percent": round(total_ratio, 3),
            "bone_threshold": round(bone_thr, 2),
        },
        "warnings": warnings,
    }


def save_results(result: dict[str, Any], output_dir: str | Path) -> dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    images = {
        "01_enhanced.png": result["enhanced_image"],
        "02_analysis_window.png": result["analysis_window_mask"],
        "03_total_bone_mask.png": result["bone_mask"],
        "04_instance_labels.png": result["instance_overlay"],
        "05_ossification_candidate_mask.png": result["ossification_candidate_mask"],
        "06_ossification_overlay.png": result["ossification_overlay"],
    }
    paths = {}
    for name, arr in images.items():
        p = out / name
        if not cv2.imwrite(str(p), arr):
            raise IOError(f"Gagal menyimpan {p}")
        paths[name] = str(p)
    csv_path = out / "per_bone_measurements.csv"
    fields = [
        "instance_id", "bone_area_px", "candidate_ossification_area_px",
        "candidate_ratio_percent", "intensity_threshold"
    ]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result["per_bone"])
    paths[csv_path.name] = str(csv_path)

    summary_path = out / "summary.json"
    import json
    summary_path.write_text(json.dumps({
        "summary": result["summary"], "warnings": result["warnings"]
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    paths[summary_path.name] = str(summary_path)
    return paths
