
from pathlib import Path

import cv2
import pymupdf as fitz
import numpy as np

from config import RAW_DATA_DIR, PROCESSED_DATA_DIR


def load_omr_image(file_path):
    """
    Load an OMR sheet from PDF or image format.
    Return an OpenCV-compatible BGR image.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = file_path.suffix.lower()

    # PDF processing
    if extension == ".pdf":

        document = fitz.open(str(file_path))

        if len(document) == 0:
            raise ValueError("PDF contains no pages.")

        page = document.load_page(0)

        # Render PDF page at higher resolution
        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(2, 2),
            alpha=False
        )

        image = np.frombuffer(
            pixmap.samples,
            dtype=np.uint8
        )

        image = image.reshape(
            pixmap.height,
            pixmap.width,
            pixmap.n
        )

        # Convert RGB to BGR for OpenCV
        image = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2BGR
        )

        document.close()

    # Normal image processing
    elif extension in [".jpg", ".jpeg", ".png", ".bmp"]:

        image = cv2.imread(str(file_path))

        if image is None:
            raise ValueError("Unable to read image.")

    else:
        raise ValueError(
            f"Unsupported file format: {extension}"
        )

    return image


def main():

    input_file = RAW_DATA_DIR / "standard_100_question_omr_filled.pdf"

    image = load_omr_image(input_file)

    height, width, channels = image.shape

    print("OMR image loaded successfully!")
    print(f"Image width: {width} pixels")
    print(f"Image height: {height} pixels")
    print(f"Channels: {channels}")

    # Save preview
    output_file = (
        PROCESSED_DATA_DIR / "omr_loaded_preview.png"
    )

    cv2.imwrite(str(output_file), image)

    print(f"Preview saved at: {output_file}")


if __name__ == "__main__":
    main()
