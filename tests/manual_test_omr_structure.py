
import sys
from pathlib import Path

import cv2
import numpy as np
import pymupdf

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.omr_structure_detector import (
    detect_omr_structure,
    draw_detected_structure
)


# ==========================================
# SMARTOMR AI - STRUCTURE DETECTOR TEST
# ==========================================

PDF_PATH = (
    PROJECT_ROOT /
    "data" / "raw" /
    "standard_100_question_omr_filled.pdf"
)

OUTPUT_PATH = (
    PROJECT_ROOT /
    "data" / "processed" /
    "omr_structure_preview_v2.png"
)


# ==========================================
# LOAD PDF
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
# RUN STRUCTURE DETECTION
# ==========================================

def run_test():

    print("\n===================================")
    print(" SMARTOMR AI - STRUCTURE DETECTOR")
    print("===================================\n")

    # Step 1: Load PDF
    print("Step 1: Loading OMR PDF...")

    image = load_pdf_image(PDF_PATH)

    print("PDF loaded successfully!")
    print("Image dimensions:", image.shape)

    # Step 2: Detect structure
    print("\nStep 2: Detecting OMR structure...")

    result = detect_omr_structure(
        image,
        expected_options=4,
        row_tolerance=12
    )

    # Step 3: Print results
    print("\n========== STRUCTURE RESULTS ==========")

    print("Layout ID:", result["layout_id"])

    print("Total Questions:", result["total_questions"])

    print("Total Columns:", result["total_columns"])

    print("Questions Per Column:", result["total_rows"])

    print("Expected Bubble Positions:",
          result["expected_bubble_positions"])

    print("Detected Bubble Positions:",
          result["detected_bubble_positions"])

    print("Missing Bubble Positions:",
          result["missing_bubble_positions"])

    print("Complete Question Groups:",
          result["detected_question_groups"])

    print("Left Column Complete:",
          result["left_column_complete_questions"])

    print("Right Column Complete:",
          result["right_column_complete_questions"])

    print("Detected Physical Rows:",
          result["total_detected_rows"])

    print("Requires Calibration:",
          result["requires_calibration"])

    # Step 4: Print incomplete questions
    print("\n========== INCOMPLETE QUESTIONS ==========")

    incomplete_questions = [
        group
        for group in result["question_groups"]
        if not group["complete"]
    ]

    if incomplete_questions:

        for group in incomplete_questions[:20]:

            print(
                f"Question {group['question_number']}: "
                f"{group['detected_options']}/"
                f"{group['expected_options']} bubbles detected"
            )

        if len(incomplete_questions) > 20:
            print(
                "Additional incomplete questions:",
                len(incomplete_questions) - 20
            )

    else:

        print("All question groups are complete.")

    # Step 5: Generate visualization
    print("\nStep 5: Generating visualization...")

    preview = draw_detected_structure(
        image,
        result["bubble_positions"],
        str(OUTPUT_PATH)
    )

    print("Visualization saved:", OUTPUT_PATH)

    # Step 6: Final validation
    print("\n========== FINAL VALIDATION ==========")

    if result["detected_bubble_positions"] == 400:

        print("SUCCESS: All 400 bubble positions detected.")

    else:

        print(
            "WARNING: Expected 400 bubble positions, but detected",
            result["detected_bubble_positions"]
        )

    if result["detected_question_groups"] == 100:

        print("SUCCESS: All 100 question groups are complete.")

    else:

        print(
            "WARNING: Complete question groups:",
            result["detected_question_groups"],
            "/ 100"
        )

    print("\nStructure detection test completed.")


if __name__ == "__main__":

    run_test()
