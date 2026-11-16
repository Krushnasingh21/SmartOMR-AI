
import sys
from pathlib import Path

import cv2
import numpy as np
import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.registration_alignment import align_omr_image
from src.bubble_detection import detect_all_answers


PROJECT_DIR = Path(__file__).resolve().parents[1]

PDF_PATH = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "standard_100_question_omr_filled.pdf"
)

OUTPUT_DIR = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "robustness_tests"
)

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


def load_omr_image():

    if not PDF_PATH.exists():
        raise FileNotFoundError(PDF_PATH)

    document = pymupdf.open(str(PDF_PATH))

    page = document[0]

    pix = page.get_pixmap(
        matrix=pymupdf.Matrix(2, 2),
        alpha=False
    )

    image = np.frombuffer(
        pix.samples,
        dtype=np.uint8
    ).reshape(pix.height, pix.width, pix.n)

    image = cv2.cvtColor(
        image,
        cv2.COLOR_RGB2BGR
    )

    document.close()

    return image


def rotate_image(image, angle):

    height, width = image.shape[:2]

    center = (width // 2, height // 2)

    matrix = cv2.getRotationMatrix2D(
        center,
        angle,
        1.0
    )

    return cv2.warpAffine(
        image,
        matrix,
        (width, height),
        borderValue=(255, 255, 255)
    )


def main():

    print("=" * 48)
    print(" SMARTOMR AI - ROTATION ALIGNMENT TEST")
    print("=" * 48)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Load original OMR image
    image = load_omr_image()

    # Rotate image by 2 degrees
    rotated_image = rotate_image(
        image,
        2
    )

    cv2.imwrite(
        str(OUTPUT_DIR / "rotation_2_degrees.png"),
        rotated_image
    )

    print("\nApplying registration alignment...")

    try:

        aligned_image = align_omr_image(
            rotated_image
        )

        cv2.imwrite(
            str(OUTPUT_DIR / "rotation_aligned.png"),
            aligned_image
        )

        print("\nAlignment completed successfully!")

    except Exception as error:

        print("\nALIGNMENT FAILED")
        print("Error:", error)
        return

    # Run bubble detection
    print("\nRunning bubble detection...")

    results = detect_all_answers(
        aligned_image
    )

    correct = 0
    wrong = 0
    review = 0
    unanswered = 0

    print("\nANSWER VERIFICATION")
    print("-" * 48)

    for question, expected in EXPECTED_ANSWERS.items():

        detected = results[question]["answer"]

        if detected == expected:
            correct += 1
        elif detected == "REVIEW_REQUIRED":
            review += 1
        elif detected == "UNANSWERED":
            unanswered += 1
        else:
            wrong += 1

        print(
            f"Q{question}: Expected={expected}, "
            f"Detected={detected}"
        )

    accuracy = correct / 10 * 100

    print("\n" + "=" * 48)
    print(" ROTATION ALIGNMENT TEST SUMMARY")
    print("=" * 48)

    print(f"Correct:    {correct}/10")
    print(f"Wrong:      {wrong}")
    print(f"Review:     {review}")
    print(f"Unanswered: {unanswered}")
    print(f"Accuracy:   {accuracy:.2f}%")

    if correct == 10:
        print("\nSUCCESS: All answers detected correctly!")
    else:
        print("\nFurther alignment improvements are required.")

    print("\nAligned image:")
    print(OUTPUT_DIR / "rotation_aligned.png")


if __name__ == "__main__":
    main()
