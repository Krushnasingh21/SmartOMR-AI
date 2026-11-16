
import cv2
import pymupdf
import numpy as np

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.layout_detector import (
    detect_layout,
    detect_registration_markers
)


# ==========================================
# SMARTOMR AI - LAYOUT DETECTOR TEST
# ==========================================

PDF_PATH = "data/raw/standard_100_question_omr_filled.pdf"


def load_pdf_image(pdf_path):

    """
    Load the first page of a PDF and convert
    it into an OpenCV BGR image.
    """

    document = pymupdf.open(pdf_path)

    page = document[0]

    pix = page.get_pixmap(
        matrix=pymupdf.Matrix(2, 2),
        alpha=False
    )

    image = np.frombuffer(
        pix.samples,
        dtype=np.uint8
    ).reshape(
        pix.height,
        pix.width,
        pix.n
    )

    image = cv2.cvtColor(
        image,
        cv2.COLOR_RGB2BGR
    )

    document.close()

    return image


def run_test():

    print("\n===================================")
    print(" SMARTOMR AI - LAYOUT DETECTOR TEST")
    print("===================================\n")

    # Load OMR PDF
    print("Step 1: Loading OMR PDF...")

    image = load_pdf_image(PDF_PATH)

    print("PDF loaded successfully!")
    print("Image dimensions:", image.shape)

    # Detect registration markers
    print("\nStep 2: Detecting registration markers...")

    markers = detect_registration_markers(image)

    print("Candidate markers detected:", len(markers))

    # Identify layout
    print("\nStep 3: Identifying OMR layout...")

    result = detect_layout(image)

    print("\n========== DETECTION RESULT ==========")

    for key, value in result.items():

        print(f"{key}: {value}")

    print("======================================")

    # Final status
    if result["registration_markers_detected"]:

        print("\nSUCCESS: Four corner markers detected.")

    else:

        print("\nWARNING: Registration markers not detected.")

    if result["layout_id"] == "smartomr_standard_100":

        print("Standard layout candidate identified.")

    else:

        print("Unknown layout. Manual calibration required.")

    print("\nLayout detection test completed.")


if __name__ == "__main__":

    run_test()
