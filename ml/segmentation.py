"""
Segmentasi eksploratif ROI X-ray OSSIA.

Membandingkan Otsu dan adaptive threshold setelah opsi denoising ringan.
Tidak mengidentifikasi anatomi secara otomatis dan bukan segmentasi klinis tervalidasi.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional
import cv2
import numpy as np


def prepare_grayscale(image: np.ndarray) -> np.ndarray:
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Citra kosong atau tidak valid.")
    if image.ndim == 3:
        if image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        elif image.shape[2] == 1:
            image = image[:, :, 0]
        else:
            raise ValueError("Jumlah channel tidak didukung.")
    elif image.ndim != 2:
        raise ValueError("Citra harus 2D grayscale atau 3D warna.")
    if image.dtype != np.uint8:
        image = np.nan_to_num(image, nan=0, posinf=255, neginf=0)
        image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return image


def denoise_image(image: np.ndarray, method: str = "median", strength: int = 3) -> np.ndarray:
    gray = prepare_grayscale(image)
    if method == "none":
        return gray.copy()
    if strength < 3 or strength % 2 == 0:
        raise ValueError("strength harus ganjil dan minimal 3.")
    if method == "median":
        return cv2.medianBlur(gray, strength)
    if method == "gaussian":
        return cv2.GaussianBlur(gray, (strength, strength), 0)
    if method == "bilateral":
        return cv2.bilateralFilter(gray, d=5, sigmaColor=35, sigmaSpace=35)
    raise ValueError("method: none, median, gaussian, bilateral.")


def otsu_segmentation(image: np.ndarray, invert: bool = False, blur_kernel: int = 3) -> Dict[str, Any]:
    gray = prepare_grayscale(image)
    if blur_kernel < 1 or blur_kernel % 2 == 0:
        raise ValueError("blur_kernel harus ganjil positif.")
    filtered = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0) if blur_kernel > 1 else gray
    flag = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
    threshold, mask = cv2.threshold(filtered, 0, 255, flag + cv2.THRESH_OTSU)
    return {"mask": mask, "threshold": float(threshold), "method": "otsu"}


def adaptive_mean_segmentation(image: np.ndarray, block_size: int = 31, c_value: int = 5, invert: bool = False) -> np.ndarray:
    gray = prepare_grayscale(image)
    _validate_adaptive(gray, block_size)
    flag = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, flag, block_size, float(c_value))


def adaptive_gaussian_segmentation(image: np.ndarray, block_size: int = 31, c_value: int = 5, invert: bool = False) -> np.ndarray:
    gray = prepare_grayscale(image)
    _validate_adaptive(gray, block_size)
    flag = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, flag, block_size, float(c_value))


def _validate_adaptive(gray: np.ndarray, block_size: int) -> None:
    if block_size <= 1 or block_size % 2 == 0:
        raise ValueError("block_size harus ganjil dan lebih besar dari 1.")
    if block_size > min(gray.shape):
        raise ValueError("block_size melebihi dimensi terkecil citra.")


def segmentation_summary(mask: np.ndarray) -> Dict[str, float]:
    if mask is None or mask.ndim != 2:
        raise ValueError("Mask harus berupa citra 2D.")
    fg = int(np.count_nonzero(mask))
    total = int(mask.size)
    return {"total_pixels": total, "foreground_pixels": fg,
            "background_pixels": total - fg, "foreground_ratio": fg / total if total else 0.0}


def segment_roi(
    image: np.ndarray,
    *,
    denoise: str = "median",
    denoise_strength: int = 3,
    invert: bool = False,
    adaptive_block_size: int = 31,
    adaptive_c: int = 5,
) -> Dict[str, Any]:
    gray = prepare_grayscale(image)
    filtered = denoise_image(gray, denoise, denoise_strength)
    otsu = otsu_segmentation(filtered, invert=invert, blur_kernel=1)
    mean = adaptive_mean_segmentation(filtered, adaptive_block_size, adaptive_c, invert)
    gaussian = adaptive_gaussian_segmentation(filtered, adaptive_block_size, adaptive_c, invert)
    masks = {"otsu": otsu["mask"], "adaptive_mean": mean, "adaptive_gaussian": gaussian}
    return {
        "gray_image": gray, "filtered_image": filtered, "masks": masks,
        "otsu_threshold": otsu["threshold"],
        "summaries": {name: segmentation_summary(mask) for name, mask in masks.items()},
        "settings": {"denoise": denoise, "denoise_strength": denoise_strength,
                     "invert": invert, "adaptive_block_size": adaptive_block_size, "adaptive_c": adaptive_c}
    }


def save_segmentation_results(image: np.ndarray, result: Dict[str, Any], output_dir: str | Path = "outputs/segmentation") -> Dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    images = {"roi_input": prepare_grayscale(image),
              "filtered_input": result["filtered_image"],
              **{f"mask_{k}": v for k, v in result["masks"].items()}}
    paths = {}
    for name, arr in images.items():
        path = out / f"{name}.png"
        if not cv2.imwrite(str(path), arr):
            raise IOError(f"Gagal menyimpan {path}")
        paths[name] = path.as_posix()
    return paths
