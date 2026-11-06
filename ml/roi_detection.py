"""
Pemilihan Region of Interest (ROI) semi-manual untuk OSSIA.

Gambar besar otomatis diperkecil untuk tampilan pemilihan ROI.
Koordinat yang disimpan tetap dikonversi ke ukuran citra asli.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import json

import cv2
import numpy as np


def load_grayscale_image(image_path: str | Path) -> np.ndarray:
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"File citra tidak ditemukan: {path}")

    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Citra tidak dapat dibaca: {path}")
    return image


def validate_roi(
    image: np.ndarray,
    roi: Tuple[int, int, int, int],
) -> Tuple[int, int, int, int]:
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Citra kosong atau tidak valid.")
    if len(roi) != 4:
        raise ValueError("ROI harus berupa (x, y, width, height).")

    x, y, width, height = (int(v) for v in roi)
    image_height, image_width = image.shape[:2]

    if x < 0 or y < 0 or width <= 0 or height <= 0:
        raise ValueError("Koordinat dan ukuran ROI harus positif.")
    if x + width > image_width or y + height > image_height:
        raise ValueError("ROI berada di luar batas citra.")

    return x, y, width, height


def crop_roi(image: np.ndarray, roi: Tuple[int, int, int, int]) -> np.ndarray:
    x, y, width, height = validate_roi(image, roi)
    return image[y:y + height, x:x + width].copy()


def create_roi_preview(
    image: np.ndarray,
    roi: Tuple[int, int, int, int],
) -> np.ndarray:
    x, y, width, height = validate_roi(image, roi)
    if image.ndim == 2:
        preview = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        preview = image.copy()

    cv2.rectangle(
        preview,
        (x, y),
        (x + width - 1, y + height - 1),
        (0, 255, 0),
        max(2, round(min(image.shape[:2]) / 700)),
    )
    return preview


def select_roi_interactively(
    image: np.ndarray,
    window_name: str = "Pilih ROI tulang karpal",
    max_display_width: int = 1200,
    max_display_height: int = 800,
) -> Tuple[int, int, int, int]:
    """
    Memilih ROI pada gambar yang sudah disesuaikan dengan ukuran layar.
    Hasil koordinat dikembalikan dalam ukuran citra asli.
    """
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Citra kosong atau tidak valid.")

    original_height, original_width = image.shape[:2]
    scale = min(
        max_display_width / original_width,
        max_display_height / original_height,
        1.0,
    )

    if scale < 1.0:
        display_width = max(1, int(round(original_width * scale)))
        display_height = max(1, int(round(original_height * scale)))
        display_image = cv2.resize(
            image,
            (display_width, display_height),
            interpolation=cv2.INTER_AREA,
        )
    else:
        display_image = image.copy()

    print(
        f"Ukuran asli: {original_width} x {original_height} | "
        f"Ukuran tampilan: {display_image.shape[1]} x {display_image.shape[0]}"
    )
    print("Tarik kotak dengan mouse, lalu tekan ENTER/SPACE untuk menerima.")
    print("Tekan C atau ESC jika ingin membatalkan.")

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(
        window_name,
        display_image.shape[1],
        display_image.shape[0],
    )

    try:
        selected = cv2.selectROI(
            window_name,
            display_image,
            showCrosshair=True,
            fromCenter=False,
        )
    finally:
        cv2.destroyAllWindows()

    x_display, y_display, w_display, h_display = (int(v) for v in selected)
    if w_display <= 0 or h_display <= 0:
        raise RuntimeError(
            "ROI belum dipilih. Tarik kotak pada gambar, lalu tekan ENTER."
        )

    # Konversi koordinat tampilan ke koordinat citra asli.
    x = int(round(x_display / scale))
    y = int(round(y_display / scale))
    width = int(round(w_display / scale))
    height = int(round(h_display / scale))

    # Jaga agar batas ROI tidak melewati ukuran citra asli.
    x = max(0, min(x, original_width - 1))
    y = max(0, min(y, original_height - 1))
    width = min(width, original_width - x)
    height = min(height, original_height - y)

    return validate_roi(image, (x, y, width, height))


def save_roi_result(
    image: np.ndarray,
    roi: Tuple[int, int, int, int],
    output_dir: str | Path = "outputs/roi",
    source_image: Optional[str] = None,
) -> Dict[str, Any]:
    x, y, width, height = validate_roi(image, roi)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    roi_image = crop_roi(image, (x, y, width, height))
    preview = create_roi_preview(image, (x, y, width, height))

    roi_file = output_path / "carpal_roi.png"
    preview_file = output_path / "roi_preview.png"
    json_file = output_path / "roi_coordinates.json"

    if not cv2.imwrite(str(roi_file), roi_image):
        raise IOError(f"Gagal menyimpan ROI: {roi_file}")
    if not cv2.imwrite(str(preview_file), preview):
        raise IOError(f"Gagal menyimpan preview ROI: {preview_file}")

    metadata = {
        "source_image": source_image,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "image_width": int(image.shape[1]),
        "image_height": int(image.shape[0]),
        "roi_file": roi_file.as_posix(),
        "preview_file": preview_file.as_posix(),
        "coordinate_convention": "pixel; origin top-left; x rightward; y downward",
    }
    json_file.write_text(
        json.dumps(metadata, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "roi_image": roi_image,
        "preview_image": preview,
        "metadata": metadata,
        "roi_path": roi_file,
        "preview_path": preview_file,
        "metadata_path": json_file,
    }
