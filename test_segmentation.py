"""Uji segmentasi ROI OSSIA.

Jalankan:
python test_segmentation.py "outputs/roi/carpal_roi.png"
"""
import argparse
from pathlib import Path
import cv2
from ml.segmentation import segment_roi, save_segmentation_results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("--denoise", choices=["none", "median", "gaussian", "bilateral"], default="median")
    parser.add_argument("--invert", action="store_true")
    parser.add_argument("--block-size", type=int, default=31)
    parser.add_argument("--c-value", type=int, default=5)
    args = parser.parse_args()

    path = Path(args.image)
    if not path.is_file():
        raise SystemExit(f"File tidak ditemukan: {path}")
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise SystemExit("Gambar tidak dapat dibaca.")

    result = segment_roi(image, denoise=args.denoise, invert=args.invert,
                         adaptive_block_size=args.block_size, adaptive_c=args.c_value)
    saved = save_segmentation_results(image, result)
    print("SEGMENTASI BERHASIL")
    print(f"ROI: {image.shape[1]} x {image.shape[0]}")
    print(f"Threshold Otsu: {result['otsu_threshold']:.2f}")
    for name, stats in result["summaries"].items():
        print(f"{name}: foreground ratio={stats['foreground_ratio']:.4f}")
    for name, filename in saved.items():
        print(f"{name}: {filename}")
    print("Mask thresholding bukan segmentasi anatomi tervalidasi.")

if __name__ == "__main__":
    main()
