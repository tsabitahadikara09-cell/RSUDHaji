"""
Uji pemilihan ROI semi-manual OSSIA.

Jalankan:
python test_roi_detection.py "outputs/preprocessing/03_preprocessed.png"

Cara memilih:
1. Jendela citra akan terbuka.
2. Klik dan tarik kotak di area tulang karpal/pergelangan tangan.
3. Tekan ENTER atau SPACE untuk menyimpan pilihan.
4. Tekan C atau ESC untuk membatalkan.
"""

import sys
from pathlib import Path

from ml.roi_detection import (
    load_grayscale_image,
    select_roi_interactively,
    save_roi_result,
)


def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            'Gunakan: python test_roi_detection.py "outputs/preprocessing/03_preprocessed.png"'
        )

    image_path = Path(sys.argv[1])
    image = load_grayscale_image(image_path)

    print("Citra berhasil dibaca.")
    print(f"Resolusi: {image.shape[1]} x {image.shape[0]}")
    print("Pilih area pergelangan/tulang karpal pada jendela yang muncul.")

    roi = select_roi_interactively(image)
    result = save_roi_result(
        image,
        roi,
        output_dir="outputs/roi",
        source_image=str(image_path),
    )

    print("\nROI BERHASIL DISIMPAN")
    print(f"Koordinat x       : {result['metadata']['x']}")
    print(f"Koordinat y       : {result['metadata']['y']}")
    print(f"Lebar ROI         : {result['metadata']['width']}")
    print(f"Tinggi ROI        : {result['metadata']['height']}")
    print(f"Citra ROI         : {result['roi_path']}")
    print(f"Preview           : {result['preview_path']}")
    print(f"Koordinat JSON    : {result['metadata_path']}")


if __name__ == "__main__":
    main()
