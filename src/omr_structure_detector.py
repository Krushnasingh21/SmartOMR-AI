
import cv2
import numpy as np
from collections import defaultdict
from pathlib import Path


# ==========================================
# SMARTOMR AI - TEMPLATE-BASED STRUCTURE DETECTOR
# ==========================================

# Standard A4 page dimensions in PDF points
PAGE_WIDTH = 595.2756
PAGE_HEIGHT = 841.8898

# Standard SmartOMR template configuration
ROW_START_Y = 645
ROW_GAP = 10.2

LEFT_COLUMN_X = 48
RIGHT_COLUMN_X = 310

BUBBLE_X_OFFSETS = [90, 124, 158, 192]
BUBBLE_RADIUS = 4.5

TOTAL_QUESTIONS = 100
QUESTIONS_PER_COLUMN = 50

OPTIONS = ["A", "B", "C", "D"]


# ==========================================
# 1. GENERATE EXPECTED BUBBLE POSITIONS
# ==========================================

def generate_expected_bubbles(image_shape):
    """
    Generate the expected positions of all 400 bubbles
    using the known SmartOMR standard template geometry.
    """

    height, width = image_shape[:2]

    scale_x = width / PAGE_WIDTH
    scale_y = height / PAGE_HEIGHT

    scale = (scale_x + scale_y) / 2

    expected_bubbles = []

    for question_number in range(1, TOTAL_QUESTIONS + 1):

        if question_number <= QUESTIONS_PER_COLUMN:

            column = "left"
            base_x = LEFT_COLUMN_X

            row_index = question_number - 1

        else:

            column = "right"
            base_x = RIGHT_COLUMN_X

            row_index = question_number - QUESTIONS_PER_COLUMN - 1

        # Convert PDF bottom-origin Y coordinate
        # into image top-origin Y coordinate.
        pdf_y = ROW_START_Y - (row_index * ROW_GAP)

        pixel_y = (PAGE_HEIGHT - pdf_y) * scale_y

        for option_index, option in enumerate(OPTIONS):

            pdf_x = base_x + BUBBLE_X_OFFSETS[option_index]

            pixel_x = pdf_x * scale_x

            expected_bubbles.append({
                "question_number": question_number,
                "column": column,
                "option": option,
                "option_index": option_index,
                "x": int(round(pixel_x)),
                "y": int(round(pixel_y)),
                "radius": max(3, int(round(BUBBLE_RADIUS * scale))),
                "detected": False,
                "ring_fill_ratio": 0.0
            })

    return expected_bubbles


# ==========================================
# 2. VALIDATE EXPECTED BUBBLE POSITIONS
# ==========================================

def calculate_ring_fill_ratio(gray, center_x, center_y, radius):
    """
    Measure dark pixels around the expected bubble outline.

    Uses an annular region to avoid relying on arbitrary
    circular contours elsewhere on the page.
    """

    height, width = gray.shape[:2]

    outer_radius = max(3, int(round(radius * 1.15)))
    inner_radius = max(2, int(round(radius * 0.70)))

    x1 = max(0, center_x - outer_radius)
    x2 = min(width, center_x + outer_radius + 1)

    y1 = max(0, center_y - outer_radius)
    y2 = min(height, center_y + outer_radius + 1)

    roi = gray[y1:y2, x1:x2]

    if roi.size == 0:
        return 0.0

    yy, xx = np.ogrid[y1:y2, x1:x2]

    distance_squared = (
        (xx - center_x) ** 2 +
        (yy - center_y) ** 2
    )

    ring_mask = (
        (distance_squared <= outer_radius ** 2) &
        (distance_squared >= inner_radius ** 2)
    )

    ring_pixels = roi[ring_mask]

    if ring_pixels.size == 0:
        return 0.0

    dark_pixels = np.count_nonzero(ring_pixels < 160)

    return float(dark_pixels / ring_pixels.size)


def detect_bubble_candidates(image):
    """
    Validate the expected 400 bubble locations.

    Returns only positions where a sufficiently dark
    circular outline is detected.
    """

    if image is None:
        raise ValueError("Input image is empty.")

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    expected_bubbles = generate_expected_bubbles(
        image.shape
    )

    detected_bubbles = []

    for bubble in expected_bubbles:

        fill_ratio = calculate_ring_fill_ratio(
            gray,
            bubble["x"],
            bubble["y"],
            bubble["radius"]
        )

        bubble["ring_fill_ratio"] = round(fill_ratio, 3)

        # Initial threshold; will be validated against
        # actual printed and scanned OMR samples.
        if fill_ratio >= 0.12:

            bubble["detected"] = True

            detected_bubbles.append(bubble)

    return detected_bubbles


# ==========================================
# 3. GROUP BUBBLES INTO PHYSICAL ROWS
# ==========================================

def group_bubbles_into_rows(bubbles, tolerance=12):
    """
    Group detected bubble positions by their Y coordinate.

    Each physical row should contain up to eight bubbles:
    four from the left column and four from the right.
    """

    if not bubbles:
        return []

    sorted_bubbles = sorted(
        bubbles,
        key=lambda bubble: bubble["y"]
    )

    rows = []

    for bubble in sorted_bubbles:

        assigned = False

        for row in rows:

            average_y = np.mean([
                item["y"] for item in row
            ])

            if abs(bubble["y"] - average_y) <= tolerance:

                row.append(bubble)
                assigned = True
                break

        if not assigned:

            rows.append([bubble])

    for row in rows:

        row.sort(
            key=lambda bubble: bubble["x"]
        )

    return rows


# ==========================================
# 4. GROUP BUBBLES BY QUESTION NUMBER
# ==========================================

def identify_question_groups(bubbles, expected_options=4):
    """
    Group bubble positions using their known question
    and option identifiers from the standard template.
    """

    grouped = defaultdict(list)

    for bubble in bubbles:

        grouped[bubble["question_number"]].append(bubble)

    question_groups = []

    for question_number in range(1, TOTAL_QUESTIONS + 1):

        question_bubbles = grouped.get(
            question_number,
            []
        )

        question_bubbles.sort(
            key=lambda bubble: bubble["option_index"]
        )

        detected_count = sum(
            1 for bubble in question_bubbles
            if bubble.get("detected", False)
        )

        question_groups.append({
            "question_number": question_number,
            "column": (
                "left"
                if question_number <= QUESTIONS_PER_COLUMN
                else "right"
            ),
            "expected_options": expected_options,
            "detected_options": detected_count,
            "complete": detected_count == expected_options,
            "bubbles": question_bubbles
        })

    return question_groups


# ==========================================
# 5. COMPLETE OMR STRUCTURE DETECTION
# ==========================================

def detect_omr_structure(
    image,
    expected_options=4,
    row_tolerance=12
):
    """
    Detect the known SmartOMR standard 100-question layout.

    This implementation uses template geometry rather than
    searching every printed circle on the page.
    """

    if image is None:
        raise ValueError("Please provide a valid OMR image.")

    height, width = image.shape[:2]

    if height == 0 or width == 0:
        raise ValueError("Invalid image dimensions.")

    if expected_options != 4:
        raise ValueError(
            "The current standard template supports four options."
        )

    page_ratio = width / float(height)

    expected_ratio = PAGE_WIDTH / PAGE_HEIGHT

    ratio_difference = abs(
        page_ratio - expected_ratio
    )

    if ratio_difference > 0.06:

        return {
            "layout_id": "unknown",
            "layout_name": "Unknown OMR Layout",
            "total_questions": 0,
            "total_columns": 0,
            "total_rows": 0,
            "expected_bubble_positions": 0,
            "detected_bubble_positions": 0,
            "detected_question_groups": 0,
            "requires_calibration": True,
            "message": (
                "Image proportions do not match the "
                "standard A4 portrait template. "
                "Alignment or manual calibration is required."
            )
        }

    # Generate all expected positions
    expected_bubbles = generate_expected_bubbles(
        image.shape
    )

    # Validate expected positions against the image
    detected_bubbles = detect_bubble_candidates(image)

    detected_lookup = {
        (
            bubble["question_number"],
            bubble["option"]
        ): bubble
        for bubble in detected_bubbles
    }

    for bubble in expected_bubbles:

        key = (
            bubble["question_number"],
            bubble["option"]
        )

        detected = detected_lookup.get(key)

        if detected:

            bubble["detected"] = True

            bubble["ring_fill_ratio"] = (
                detected["ring_fill_ratio"]
            )

    # Group all expected positions by question
    question_groups = identify_question_groups(
        expected_bubbles,
        expected_options=expected_options
    )

    # Count complete questions
    complete_questions = sum(
        1 for group in question_groups
        if group["complete"]
    )

    # Group detected bubbles into physical rows
    detected_rows = group_bubbles_into_rows(
        detected_bubbles,
        tolerance=row_tolerance
    )

    left_complete = sum(
        1 for group in question_groups
        if group["column"] == "left" and group["complete"]
    )

    right_complete = sum(
        1 for group in question_groups
        if group["column"] == "right" and group["complete"]
    )

    total_detected = len(detected_bubbles)

    total_expected = len(expected_bubbles)

    return {
        "layout_id": "smartomr_standard_100",
        "layout_name": "SmartOMR Standard 100 Question Layout",

        "total_questions": TOTAL_QUESTIONS,
        "total_columns": 2,
        "total_rows": QUESTIONS_PER_COLUMN,

        "expected_options": expected_options,

        "expected_bubble_positions": total_expected,
        "detected_bubble_positions": total_detected,
        "missing_bubble_positions": (
            total_expected - total_detected
        ),

        "detected_question_groups": complete_questions,
        "left_column_complete_questions": left_complete,
        "right_column_complete_questions": right_complete,

        "total_detected_rows": len(detected_rows),

        "question_groups": question_groups,
        "bubble_positions": expected_bubbles,

        "requires_calibration": False,

        "message": (
            "Standard template geometry identified. "
            "Bubble position validation completed."
        )
    }


# ==========================================
# 6. VISUALIZE DETECTED STRUCTURE
# ==========================================

def draw_detected_structure(image, bubbles, output_path=None):
    """
    Draw validated bubble positions in green
    and missing expected positions in red.
    """

    if image is None:
        raise ValueError("Input image is empty.")

    output = image.copy()

    for bubble in bubbles:

        center = (
            int(bubble["x"]),
            int(bubble["y"])
        )

        radius = int(bubble["radius"])

        if bubble.get("detected", False):

            color = (0, 255, 0)

        else:

            color = (0, 0, 255)

        cv2.circle(
            output,
            center,
            radius,
            color,
            2
        )

    if output_path:

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        success = cv2.imwrite(
            str(output_path),
            output
        )

        if not success:

            raise IOError(
                f"Unable to save visualization: {output_path}"
            )

    return output


# ==========================================
# 7. MODULE TEST
# ==========================================

if __name__ == "__main__":

    print("===================================")
    print("          SMARTOMR AI")
    print("     TEMPLATE STRUCTURE DETECTOR")
    print("===================================")

    print("Standard template configuration loaded.")
    print("Expected questions:", TOTAL_QUESTIONS)
    print("Expected columns: 2")
    print("Expected options per question:", len(OPTIONS))
    print(
        "Expected bubble positions:",
        TOTAL_QUESTIONS * len(OPTIONS)
    )

    print("\nStructure detector ready.")
