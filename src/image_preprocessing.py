
import cv2
from pathlib import Path

from config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.image_loader import load_omr_image


# ==========================================
# 1. GRAYSCALE CONVERSION
# ==========================================

def convert_to_grayscale(image):
    """
    Convert the original BGR image into grayscale.
    """

    grayscale = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return grayscale


# ==========================================
# 2. GAUSSIAN BLUR
# ==========================================

def apply_gaussian_blur(grayscale):
    """
    Remove small image noise using Gaussian Blur.
    """

    blurred = cv2.GaussianBlur(
        grayscale,
        (5, 5),
        0
    )

    return blurred


# ==========================================
# 3. IMAGE THRESHOLDING
# ==========================================

def apply_thresholding(blurred):
    """
    Convert grayscale image into a binary image
    using Otsu's thresholding method.
    """

    threshold_value, threshold_image = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    print(f"Calculated threshold value: {threshold_value}")

    return threshold_image


# ==========================================
# 4. SAVE PROCESSED IMAGES
# ==========================================

def save_processed_image(image, filename):

    output_path = PROCESSED_DATA_DIR / filename

    success = cv2.imwrite(
        str(output_path),
        image
    )

    if not success:
        raise IOError(f"Could not save image: {output_path}")

    print(f"Saved: {output_path}")


# ==========================================
# 5. MAIN PROCESSING FUNCTION
# ==========================================

def main():

    input_file = RAW_DATA_DIR / "standard_100_question_omr_filled.pdf"

    # Load original OMR image
    original_image = load_omr_image(input_file)

    print("\nOriginal image loaded successfully!")

    # Convert to grayscale
    grayscale = convert_to_grayscale(original_image)

    print("Grayscale conversion completed!")

    # Apply Gaussian Blur
    blurred = apply_gaussian_blur(grayscale)

    print("Gaussian Blur applied successfully!")

    # Apply thresholding
    threshold_image = apply_thresholding(blurred)

    print("Thresholding completed!")

    # Save all processed images
    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    save_processed_image(
        grayscale,
        "omr_grayscale.png"
    )

    save_processed_image(
        blurred,
        "omr_blurred.png"
    )

    save_processed_image(
        threshold_image,
        "omr_threshold.png"
    )

    print("\nAll preprocessing operations completed!")


# ==========================================
# 6. EXECUTION
# ==========================================

if __name__ == "__main__":
    main()
