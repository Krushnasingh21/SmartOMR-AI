
import cv2
import numpy as np

from config import PROCESSED_DATA_DIR



# ==========================================
# 1. TEMPLATE CONFIGURATION
# ==========================================

TOTAL_QUESTIONS = 100

OPTIONS = ["A", "B", "C", "D"]

QUESTIONS_PER_COLUMN = 50

# Original PDF dimensions in points (A4)
PDF_WIDTH = 595.2756
PDF_HEIGHT = 841.8898

# Original template coordinates in PDF points
ROW_START_Y = 645
ROW_GAP = 10.2

BUBBLE_RADIUS = 4.5

COLUMN_STARTS = [48, 310]

BUBBLE_OFFSETS = [90, 124, 158, 192]

EMPTY_THRESHOLD = 20.0
FILLED_THRESHOLD = 45.0



# ==========================================
# 2. LOAD ALIGNED OMR IMAGE
# ==========================================


def load_omr_image():

    image_path = PROCESSED_DATA_DIR / "omr_grayscale.png"

    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise FileNotFoundError(
            f"Original grayscale image not found: {image_path}"
        )

    return image



# ==========================================
# 3. CALCULATE BUBBLE FILL PERCENTAGE
# ==========================================


def calculate_fill_percentage(image, center, radius):

    x, y = map(int, center)

    padding = radius + 3

    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(image.shape[1], x + padding + 1)
    y2 = min(image.shape[0], y + padding + 1)

    roi = image[y1:y2, x1:x2]

    if roi.size == 0:
        return 0.0

    # Create a circular mask excluding the outer outline
    mask = np.zeros(roi.shape, dtype=np.uint8)

    center_roi = (x - x1, y - y1)

    inner_radius = max(1, int(radius * 0.65))

    cv2.circle(
        mask,
        center_roi,
        inner_radius,
        255,
        -1
    )

    # Use a fixed threshold for dark pixel detection
    _, binary = cv2.threshold(
        roi,
        150,
        255,
        cv2.THRESH_BINARY_INV
    )

    dark_pixels = cv2.countNonZero(
        cv2.bitwise_and(binary, mask)
    )

    total_pixels = cv2.countNonZero(mask)

    if total_pixels == 0:
        return 0.0

    return (dark_pixels / total_pixels) * 100



# ==========================================
# 4. CLASSIFY BUBBLE
# ==========================================

def classify_bubble(fill_percentage):

    if fill_percentage < EMPTY_THRESHOLD:
        return "EMPTY"

    elif fill_percentage >= FILLED_THRESHOLD:
        return "FILLED"

    else:
        return "UNCERTAIN"


# ==========================================
# 5. DETECT ONE QUESTION
# ==========================================



def detect_question(image, question_number):

    height, width = image.shape

    # Convert PDF points into image pixels
    scale_x = width / PDF_WIDTH
    scale_y = height / PDF_HEIGHT

    if question_number <= 50:

        column_start = COLUMN_STARTS[0]
        row_index = question_number - 1

    else:

        column_start = COLUMN_STARTS[1]
        row_index = question_number - 51

    # PDF coordinates use bottom-left origin
    y_pdf = ROW_START_Y - (row_index * ROW_GAP)

    results = {}

    for option, offset in zip(OPTIONS, BUBBLE_OFFSETS):

        x_pdf = column_start + offset

        # Convert PDF coordinates to OpenCV pixel coordinates
        x_pixel = int(round(x_pdf * scale_x))
        y_pixel = int(round((PDF_HEIGHT - y_pdf) * scale_y))

        radius_x = int(round(BUBBLE_RADIUS * scale_x))
        radius_y = int(round(BUBBLE_RADIUS * scale_y))

        fill_percentage = calculate_fill_percentage(
            image,
            (x_pixel, y_pixel),
            min(radius_x, radius_y)
        )

        classification = classify_bubble(fill_percentage)

        results[option] = {
            "fill_percentage": round(fill_percentage, 2),
            "status": classification
        }

    return results


# ==========================================
# 6. EXTRACT ANSWER
# ==========================================

def extract_answer(bubble_results):

    filled_options = [
        option
        for option, result in bubble_results.items()
        if result["status"] == "FILLED"
    ]

    uncertain_options = [
        option
        for option, result in bubble_results.items()
        if result["status"] == "UNCERTAIN"
    ]

    if uncertain_options:
        return "REVIEW_REQUIRED"

    if len(filled_options) == 0:
        return "UNANSWERED"

    if len(filled_options) > 1:
        return "MULTIPLE_MARKS"

    return filled_options[0]


# ==========================================
# 7. DETECT ALL QUESTIONS
# ==========================================

def detect_all_answers(image):

    answers = {}

    for question_number in range(1, TOTAL_QUESTIONS + 1):

        bubble_results = detect_question(
            image,
            question_number
        )

        answer = extract_answer(
            bubble_results
        )

        answers[question_number] = {
            "answer": answer,
            "bubbles": bubble_results
        }

    return answers


# ==========================================
# 8. MAIN FUNCTION
# ==========================================

def main():

    print("Loading aligned OMR sheet...")

    image = load_omr_image()

    print("OMR sheet loaded successfully!")

    print("\nStarting bubble detection...")

    answers = detect_all_answers(image)

    for question_number, result in answers.items():

        print(f"Q{question_number}: {result['answer']}")

        # Show individual bubble measurements for first 10 questions
        if question_number <= 10:

            for option, details in result["bubbles"].items():

                print(
                    f"    {option}: "
                    f"{details['fill_percentage']}% "
                    f"({details['status']})"
                )

    print("\nBubble detection completed!")

# ==========================================
# 9. EXECUTION
# ==========================================

if __name__ == "__main__":
    main()
