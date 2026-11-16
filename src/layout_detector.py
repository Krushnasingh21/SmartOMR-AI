
import cv2
import numpy as np


# ==========================================
# SMARTOMR AI - UNIVERSAL LAYOUT DETECTOR
# ==========================================


def detect_registration_markers(image):
    """
    Detect square registration markers near
    the four corners of an OMR sheet.
    """

    if image is None:
        raise ValueError("Input image is empty.")

    height, width = image.shape[:2]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Convert dark regions into white foreground
    _, threshold = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    candidates = []

    min_dimension = min(width, height)

    min_size = max(8, int(min_dimension * 0.008))
    max_size = int(min_dimension * 0.06)

    for contour in contours:

        area = cv2.contourArea(contour)

        if area < min_size ** 2:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        if not (min_size <= w <= max_size):
            continue

        if not (min_size <= h <= max_size):
            continue

        aspect_ratio = w / float(h)

        if not 0.75 <= aspect_ratio <= 1.30:
            continue

        perimeter = cv2.arcLength(contour, True)

        if perimeter == 0:
            continue

        approx = cv2.approxPolyDP(
            contour,
            0.04 * perimeter,
            True
        )

        if len(approx) != 4:
            continue

        if not cv2.isContourConvex(approx):
            continue

        # Check how much of the bounding box is filled
        rectangle_area = w * h
        fill_ratio = area / float(rectangle_area)

        if fill_ratio < 0.65:
            continue

        center_x = x + w / 2
        center_y = y + h / 2

        candidates.append({
            "x": int(center_x),
            "y": int(center_y),
            "width": int(w),
            "height": int(h),
            "area": float(area)
        })

    return candidates


# ==========================================
# IDENTIFY FOUR CORNER MARKERS
# ==========================================

def identify_corner_markers(candidates, image_shape):
    """
    Identify one marker in each corner region.
    """

    height, width = image_shape[:2]

    corner_regions = {
        "top_left": [],
        "top_right": [],
        "bottom_left": [],
        "bottom_right": []
    }

    for marker in candidates:

        x = marker["x"]
        y = marker["y"]

        if x < width * 0.25 and y < height * 0.25:

            corner_regions["top_left"].append(marker)

        elif x > width * 0.75 and y < height * 0.25:

            corner_regions["top_right"].append(marker)

        elif x < width * 0.25 and y > height * 0.75:

            corner_regions["bottom_left"].append(marker)

        elif x > width * 0.75 and y > height * 0.75:

            corner_regions["bottom_right"].append(marker)

    selected_markers = {}

    for corner, markers in corner_regions.items():

        if not markers:
            return None

        selected_markers[corner] = max(
            markers,
            key=lambda marker: marker["area"]
        )

    return selected_markers


# ==========================================
# MAIN LAYOUT DETECTION
# ==========================================

def detect_layout(image):
    """
    Identify a candidate SmartOMR standard layout
    using page proportions and corner markers.

    Further question and bubble validation will
    be implemented in subsequent development steps.
    """

    if image is None:
        raise ValueError("Please provide a valid OMR image.")

    height, width = image.shape[:2]

    if height == 0 or width == 0:
        raise ValueError("Invalid image dimensions.")

    # Calculate page aspect ratio
    page_ratio = width / float(height)

    # A4 portrait aspect ratio
    expected_ratio = 210 / 297

    ratio_difference = abs(
        page_ratio - expected_ratio
    )

    # Detect registration markers
    candidates = detect_registration_markers(image)

    markers = identify_corner_markers(
        candidates,
        image.shape
    )

    # If all four markers are not detected
    if markers is None:

        return {
            "layout_id": "unknown",
            "layout_name": "Unknown OMR Layout",
            "confidence": 0.0,
            "registration_markers_detected": False,
            "marker_count": len(candidates),
            "requires_calibration": True,
            "message": (
                "Four corner registration markers "
                "could not be identified. Manual "
                "layout calibration is required."
            )
        }

    # Validate page proportions
    if ratio_difference > 0.06:

        return {
            "layout_id": "unknown",
            "layout_name": "Unknown OMR Layout",
            "confidence": 0.0,
            "registration_markers_detected": True,
            "marker_count": 4,
            "requires_calibration": True,
            "message": (
                "Registration markers were detected, "
                "but page proportions do not match "
                "the expected A4 portrait layout."
            )
        }

    # Calculate preliminary confidence
    confidence = max(
        0.0,
        1.0 - (ratio_difference / 0.06)
    )

    return {
        "layout_id": "smartomr_standard_100",
        "layout_name": "SmartOMR Standard 100 Question Layout",
        "confidence": round(confidence, 2),
        "registration_markers_detected": True,
        "marker_count": 4,
        "markers": markers,
        "requires_calibration": False,
        "message": (
            "Standard layout candidate detected. "
            "Question and bubble arrangement validation "
            "is still required."
        )
    }


# ==========================================
# TEST MODULE
# ==========================================

if __name__ == "__main__":

    print("===================================")
    print("       SMARTOMR AI")
    print("       LAYOUT DETECTOR")
    print("===================================")

    print("Layout detector module loaded successfully.")
    print("Ready for OMR layout detection.")
