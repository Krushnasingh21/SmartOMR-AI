
import sys
from pathlib import Path

import cv2
import numpy as np
import pymupdf

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.bubble_detection import (
    detect_all_answers,
    print_detection_results
)


# ==========================================
# SMARTOMR AI - BUBBLE DETECTION TEST
# ==========================================

PDF_PATH = (
    PROJECT_ROOT /
    "data" / "raw" /
    "standard_100_question_omr_filled.pdf"
)


# Expected answers from the filled sample OMR sheet
EXPECTED_ANSWERS = {
    1: "A",
    2: "C",
    3: "B",
    4: "D",
    5: "A",
    6: "B",
    7: "C",
    8: "D",
    9: "A",
    10: "C"
}


# ==========================================
# LOAD PDF IMAGE
# ==========================================

def load_pdf_image(pdf_path):

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"OMR PDF not found: {pdf_path}"
        )

    document = pymupdf.open(str(pdf_path))

    try:

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

        return image

    finally:
        document.close()


# ==========================================
# RUN BUBBLE DETECTION TEST
# ==========================================

def run_test():

    print("\n===================================")
    print(" SMARTOMR AI - BUBBLE DETECTION TEST")
    print("===================================\n")

    # Step 1: Load OMR PDF
    print("Step 1: Loading OMR PDF...")

    image = load_pdf_image(PDF_PATH)

    print("PDF loaded successfully!")
    print("Image dimensions:", image.shape)

    # Step 2: Extract answers
    print("\nStep 2: Detecting and classifying bubbles...")

    results = detect_all_answers(image)

    print("Bubble detection completed!")

    # Step 3: Print extracted answers
    print_detection_results(results)

    # Step 4: Compare expected and detected answers
    print("\n========== ANSWER VERIFICATION ==========")

    correct = 0
    incorrect = 0

    for question_number, expected in EXPECTED_ANSWERS.items():

        detected = results[question_number]["answer"]

        if detected == expected:
            status = "PASS"
            correct += 1

        else:
            status = "FAIL"
            incorrect += 1

        print(
            f"Q{question_number}: "
            f"Expected={expected}, "
            f"Detected={detected}, "
            f"Status={status}"
        )

    # Step 5: Verify unanswered questions
    print("\n========== UNANSWERED VERIFICATION ==========")

    unanswered_correct = 0
    unanswered_incorrect = 0

    for question_number in range(11, 101):

        detected = results[question_number]["answer"]

        if detected == "UNANSWERED":
            unanswered_correct += 1

        else:
            unanswered_incorrect += 1

            print(
                f"Q{question_number}: "
                f"Expected=UNANSWERED, "
                f"Detected={detected}"
            )

    # Step 6: Final summary
    print("\n========== FINAL TEST SUMMARY ==========")

    print("Correct first 10 answers:", correct)
    print("Incorrect first 10 answers:", incorrect)

    print("Correctly unanswered questions:", unanswered_correct)
    print("Incorrectly classified unanswered:", unanswered_incorrect)

    print("Total questions tested:", len(results))

    if correct == 10 and unanswered_correct == 90:

        print("\nSUCCESS: All sample answers detected correctly!")

    else:

        print("\nWARNING: Bubble classification needs improvement.")

    print("\nBubble detection test completed.")


if __name__ == "__main__":

    run_test()
