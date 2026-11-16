
import cv2
import numpy as np

from src.omr_structure_detector import generate_expected_bubbles


# ==========================================
# SMARTOMR AI - BUBBLE CLASSIFICATION
# ==========================================

OPTIONS = ["A", "B", "C", "D"]

# Initial classification thresholds
EMPTY_THRESHOLD = 20
FILLED_THRESHOLD = 45

PIXEL_THRESHOLD = 150


# ==========================================
# 1. CALCULATE BUBBLE FILL PERCENTAGE
# ==========================================

def calculate_fill_percentage(gray, bubble):
    """
    Calculate the percentage of dark pixels
    inside the bubble, excluding its outline.
    """

    height, width = gray.shape[:2]

    center_x = bubble["x"]
    center_y = bubble["y"]
    radius = bubble["radius"]

    # Use the inner area to avoid counting
    # the printed circular bubble outline.
    inner_radius = max(2, int(radius * 0.55))

    x1 = max(0, center_x - inner_radius)
    x2 = min(width, center_x + inner_radius + 1)

    y1 = max(0, center_y - inner_radius)
    y2 = min(height, center_y + inner_radius + 1)

    roi = gray[y1:y2, x1:x2]

    if roi.size == 0:
        return 0.0

    yy, xx = np.ogrid[y1:y2, x1:x2]

    distance_squared = (
        (xx - center_x) ** 2 +
        (yy - center_y) ** 2
    )

    circular_mask = (
        distance_squared <= inner_radius ** 2
    )

    bubble_pixels = roi[circular_mask]

    if bubble_pixels.size == 0:
        return 0.0

    dark_pixels = np.count_nonzero(
        bubble_pixels < PIXEL_THRESHOLD
    )

    fill_percentage = (
        dark_pixels / bubble_pixels.size
    ) * 100

    return round(float(fill_percentage), 2)


# ==========================================
# 2. CLASSIFY INDIVIDUAL BUBBLE
# ==========================================

def classify_bubble(fill_percentage):
    """
    Classify a bubble as EMPTY, FILLED or UNCERTAIN.
    """

    if fill_percentage < EMPTY_THRESHOLD:

        return "EMPTY"

    elif fill_percentage >= FILLED_THRESHOLD:

        return "FILLED"

    else:

        return "UNCERTAIN"


# ==========================================
# 3. ANALYZE ALL BUBBLES
# ==========================================

def detect_all_bubbles(image):
    """
    Analyze all 400 expected bubble positions
    using the standard OMR template geometry.
    """

    if image is None:
        raise ValueError("Input image is empty.")

    if len(image.shape) == 2:

        gray = image.copy()

    else:

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

    expected_bubbles = generate_expected_bubbles(
        gray.shape
    )

    detected_bubbles = []

    for bubble in expected_bubbles:

        fill_percentage = calculate_fill_percentage(
            gray,
            bubble
        )

        status = classify_bubble(
            fill_percentage
        )

        detected_bubbles.append({
            "question_number": bubble["question_number"],
            "column": bubble["column"],
            "option": bubble["option"],
            "x": bubble["x"],
            "y": bubble["y"],
            "fill_percentage": fill_percentage,
            "status": status
        })

    return detected_bubbles


# ==========================================
# 4. EXTRACT ANSWER FOR EACH QUESTION
# ==========================================

def extract_answer(bubble_results):
    """
    Determine the answer for one question.
    """

    filled_options = [
        bubble["option"]
        for bubble in bubble_results
        if bubble["status"] == "FILLED"
    ]

    uncertain_options = [
        bubble["option"]
        for bubble in bubble_results
        if bubble["status"] == "UNCERTAIN"
    ]

    # Uncertain marks require human review
    if uncertain_options:

        return "REVIEW_REQUIRED"

    # Multiple marked bubbles
    if len(filled_options) > 1:

        return "MULTIPLE_MARKS"

    # No marked bubble
    if len(filled_options) == 0:

        return "UNANSWERED"

    # Exactly one marked bubble
    return filled_options[0]


# ==========================================
# 5. DETECT ALL ANSWERS
# ==========================================

def detect_all_answers(image):
    """
    Extract answers for all 100 questions.

    Returns a dictionary containing the answer
    and individual bubble measurements.
    """

    bubble_results = detect_all_bubbles(image)

    question_results = {}

    for question_number in range(1, 101):

        question_bubbles = [
            bubble
            for bubble in bubble_results
            if bubble["question_number"] == question_number
        ]

        question_bubbles.sort(
            key=lambda bubble: OPTIONS.index(bubble["option"])
        )

        answer = extract_answer(question_bubbles)

        question_results[question_number] = {
            "answer": answer,
            "bubbles": question_bubbles
        }

    return question_results


# ==========================================
# 6. PRINT ANSWER EXTRACTION RESULTS
# ==========================================

def print_detection_results(results):
    """
    Print extracted answers and summary counts.
    """

    correct_format = []

    for question_number, result in results.items():

        answer = result["answer"]

        correct_format.append(
            (question_number, answer)
        )

    print("\n===================================")
    print(" SMARTOMR AI - ANSWER EXTRACTION")
    print("===================================")

    for question_number, answer in correct_format:

        print(f"Question {question_number}: {answer}")

    answered = sum(
        1 for _, answer in correct_format
        if answer in OPTIONS
    )

    unanswered = sum(
        1 for _, answer in correct_format
        if answer == "UNANSWERED"
    )

    multiple_marks = sum(
        1 for _, answer in correct_format
        if answer == "MULTIPLE_MARKS"
    )

    review_required = sum(
        1 for _, answer in correct_format
        if answer == "REVIEW_REQUIRED"
    )

    print("\n========== SUMMARY ==========")

    print("Total Questions:", len(results))
    print("Answered:", answered)
    print("Unanswered:", unanswered)
    print("Multiple Marks:", multiple_marks)
    print("Review Required:", review_required)

    print("=============================")


# ==========================================
# 7. MODULE TEST
# ==========================================

if __name__ == "__main__":

    print("===================================")
    print("          SMARTOMR AI")
    print("       BUBBLE DETECTOR")
    print("===================================")

    print("Bubble classification module loaded.")
    print("Ready for answer extraction.")
