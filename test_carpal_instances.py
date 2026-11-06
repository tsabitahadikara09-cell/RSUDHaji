"""Uji segmentasi instance tulang karpal dan kandidat osifikasi OSSIA."""
import argparse
from pathlib import Path
import cv2
from ml.carpal_instances import segment_carpal_bones_and_ossification, save_results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Path citra ROI karpal")
    parser.add_argument("--output", default="outputs/carpal_instances")
    parser.add_argument("--bone-percentile", type=float, default=42.0)
    parser.add_argument("--ossification-percentile", type=float, default=72.0)
    parser.add_argument("--bottom-fraction", type=float, default=0.86,
                        help="Batas bawah analisis sebagai fraksi tinggi ROI")
    parser.add_argument("--min-seed-distance", type=int, default=22)
    parser.add_argument("--max-instances", type=int, default=8)
    args = parser.parse_args()

    image = cv2.imread(args.image, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise SystemExit(f"Gagal membaca citra: {args.image}")
    result = segment_carpal_bones_and_ossification(
        image,
        bone_percentile=args.bone_percentile,
        ossification_percentile=args.ossification_percentile,
        roi_bottom_fraction=args.bottom_fraction,
        min_seed_distance=args.min_seed_distance,
        max_instances=args.max_instances,
    )
    paths = save_results(result, args.output)
    print("\\nSEGMENTASI INSTANCE SELESAI")
    print(f"Instance terdeteksi: {result['summary']['detected_instances']}")
    print(f"Luas mask tulang total: {result['summary']['total_bone_area_px']} px")
    print(f"Luas kandidat osifikasi: {result['summary']['total_candidate_ossification_area_px']} px")
    print(f"Rasio kandidat total: {result['summary']['total_candidate_ratio_percent']}%")
    print("\\nPer instance:")
    for row in result["per_bone"]:
        print(
            f"  Instance {row['instance_id']}: "
            f"bone={row['bone_area_px']} px | "
            f"kandidat={row['candidate_ossification_area_px']} px | "
            f"rasio={row['candidate_ratio_percent']}%"
        )
    print("\\nFile hasil:")
    for name, path in paths.items():
        print(f"  {name}: {path}")
    print("\\nPERINGATAN:")
    for warning in result["warnings"]:
        print(f"  - {warning}")

if __name__ == "__main__":
    main()
