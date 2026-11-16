
import sys
from pathlib import Path

import cv2
import numpy as np
import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.bubble_detection import detect_all_answers


PROJECT_DIR = Path(__file__).resolve().parents[1]

PDF_PATH = PROJECT_DIR / "data" / "raw" / "standard_100_question_omr_filled.pdf"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed" / "robustness_tests"

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
    10: "C",
}


def load_omr_image():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"OMR PDF not found: {PDF_PATH}")

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

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    document.close()
    return image


def create_variations(image):
    variations = {}

    # 1. Original image
    variations["Original"] = image.copy()

    # 2. Slight Gaussian blur
    variations["Blur"] = cv2.GaussianBlur(
        image, (5, 5), 0
    )

    # 3. Reduced brightness
    variations["Low_Brightness"] = cv2.convertScaleAbs(
        image, alpha=0.75, beta=-20
    )

    # 4. Increased brightness
    variations["High_Brightness"] = cv2.convertScaleAbs(
        image, alpha=1.15, beta=25
    )

    # 5. Gaussian noise
    noise = np.random.normal(
        0, 8, image.shape
    ).astype(np.float32)

    noisy_image = np.clip(
        image.astype(np.float32) + noise,
        0,
        255
    ).astype(np.uint8)

    variations["Noise"] = noisy_image

    # 6. Slight rotation
    height, width = image.shape[:2]

    center = (width // 2, height // 2)

    rotation_matrix = cv2.getRotationMatrix2D(
        center, 2, 1.0
    )

    rotated_image = cv2.warpAffine(
        image,
        rotation_matrix,
        (width, height),
        borderValue=(255, 255, 255)
    )

    variations["Rotation_2_Degrees"] = rotated_image

    return variations


def evaluate_variation(name, image):
    results = detect_all_answers(image)

    correct = 0
    wrong = 0
    review = 0
    unanswered = 0

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

    accuracy = (correct / len(EXPECTED_ANSWERS)) * 100

    print(f"\n{name}")
    print("-" * 40)
    print(f"Correct:     {correct}/10")
    print(f"Wrong:       {wrong}")
    print(f"Review:      {review}")
    print(f"Unanswered:  {unanswered}")
    print(f"Accuracy:    {accuracy:.2f}%")

    return {
        "name": name,
        "correct": correct,
        "wrong": wrong,
        "review": review,
        "unanswered": unanswered,
        "accuracy": accuracy
    }


def main():
    print("=" * 48)
    print(" SMARTOMR AI - IMAGE ROBUSTNESS TESTING")
    print("=" * 48)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    original_image = load_omr_image()

    variations = create_variations(original_image)

    all_results = []

    for name, image in variations.items():

        # Save each test image for visual inspection
        output_path = OUTPUT_DIR / f"{name}.png"

        cv2.imwrite(str(output_path), image)

        result = evaluate_variation(name, image)
        all_results.append(result)

    print("\n" + "=" * 48)
    print(" FINAL ROBUSTNESS TEST SUMMARY")
    print("=" * 48)

    for result in all_results:
        print(
            f"{result['name']:<24} "
            f"{result['correct']}/10 "
            f"({result['accuracy']:.1f}%)"
        )

    print("\nTest images saved in:")
    print(OUTPUT_DIR)

    print("\nRobustness testing completed.")


if __name__ == "__main__":
    main()
