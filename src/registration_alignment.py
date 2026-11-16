
import cv2
import numpy as np

from config import PROCESSED_DATA_DIR


# ==========================================
# CONFIGURATION
# ==========================================

PAGE_WIDTH = 595.2756
PAGE_HEIGHT = 841.8898

# Registration marker centers in PDF points
MARKER_LEFT_X = 29.0
MARKER_RIGHT_X = 566.0
MARKER_TOP_Y = 29.0
MARKER_BOTTOM_Y = 812.0


# ==========================================
# 1. LOAD GRAYSCALE IMAGE
# ==========================================

def load_grayscale_image():

    input_path = PROCESSED_DATA_DIR / "omr_grayscale.png"

    image = cv2.imread(
        str(input_path),
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise FileNotFoundError(
            f"Image not found: {input_path}"
        )

    return image


# ==========================================
# 2. DETECT REGISTRATION MARKERS
# ==========================================

def detect_registration_markers(image):

    if image is None:
        raise ValueError("Input image is empty.")

    if len(image.shape) != 2:
        raise ValueError(
            "Registration marker detection requires grayscale image."
        )

    height, width = image.shape

    # Convert dark pixels into white foreground pixels
    _, binary = cv2.threshold(
        image,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # Find connected components
    count, labels, stats, centroids = (
        cv2.connectedComponentsWithStats(
            binary,
            connectivity=8
        )
    )

    candidates = []

    # Inspect every connected component
    for index in range(1, count):

        x, y, w, h, area = stats[index]

        aspect_ratio = w / float(h)

        minimum_area = width * height * 0.00015
        maximum_area = width * height * 0.0012

        if not (minimum_area <= area <= maximum_area):
            continue

        if not (0.75 <= aspect_ratio <= 1.25):
            continue

        if w < width * 0.008 or h < height * 0.008:
            continue

        center_x, center_y = centroids[index]

        candidates.append({
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "area": area,
            "center": (center_x, center_y)
        })

    print(
        f"Square marker candidates found: {len(candidates)}"
    )

    # Divide image into four corner regions
    corner_regions = {
        "top_left": (
            0, 0, width * 0.18, height * 0.12
        ),

        "top_right": (
            width * 0.82, 0, width, height * 0.12
        ),

        "bottom_right": (
            width * 0.82,
            height * 0.88,
            width,
            height
        ),

        "bottom_left": (
            0,
            height * 0.88,
            width * 0.18,
            height
        )
    }

    detected = {}

    # Select largest suitable square in each corner
    for corner, (x1, y1, x2, y2) in corner_regions.items():

        corner_candidates = [
            candidate for candidate in candidates
            if (
                x1 <= candidate["center"][0] <= x2
                and y1 <= candidate["center"][1] <= y2
            )
        ]

        if not corner_candidates:
            raise ValueError(
                f"Registration marker not found: {corner}"
            )

        best_candidate = max(
            corner_candidates,
            key=lambda item: item["area"]
        )

        detected[corner] = best_candidate["center"]

        print(
            f"{corner}: {best_candidate['center']}"
        )

    return detected


# ==========================================
# 3. VISUALIZE REGISTRATION MARKERS
# ==========================================

def draw_registration_markers(image, markers):

    if len(image.shape) == 2:
        output = cv2.cvtColor(
            image,
            cv2.COLOR_GRAY2BGR
        )
    else:
        output = image.copy()

    for name, point in markers.items():

        x, y = map(int, point)

        cv2.circle(
            output,
            (x, y),
            12,
            (0, 0, 255),
            2
        )

        cv2.putText(
            output,
            name,
            (x + 12, y + 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 255),
            1
        )

    return output


# ==========================================
# 4. PERSPECTIVE TRANSFORMATION
# ==========================================

def correct_perspective(image, markers):

    height, width = image.shape[:2]

    # Source points in clockwise order
    source_points = np.array([
        markers["top_left"],
        markers["top_right"],
        markers["bottom_right"],
        markers["bottom_left"]
    ], dtype=np.float32)

    # Map marker centers to original template geometry
    destination_points = np.array([

        [
            width * (MARKER_LEFT_X / PAGE_WIDTH),
            height * (MARKER_TOP_Y / PAGE_HEIGHT)
        ],

        [
            width * (MARKER_RIGHT_X / PAGE_WIDTH),
            height * (MARKER_TOP_Y / PAGE_HEIGHT)
        ],

        [
            width * (MARKER_RIGHT_X / PAGE_WIDTH),
            height * (MARKER_BOTTOM_Y / PAGE_HEIGHT)
        ],

        [
            width * (MARKER_LEFT_X / PAGE_WIDTH),
            height * (MARKER_BOTTOM_Y / PAGE_HEIGHT)
        ]

    ], dtype=np.float32)

    # Calculate transformation matrix
    matrix = cv2.getPerspectiveTransform(
        source_points,
        destination_points
    )

    # Apply perspective transformation
    aligned_image = cv2.warpPerspective(
        image,
        matrix,
        (width, height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=255
    )

    return aligned_image


# ==========================================
# 5. REUSABLE IMAGE ALIGNMENT FUNCTION
# ==========================================

def align_omr_image(image):

    if image is None:
        raise ValueError(
            "Input OMR image is empty."
        )

    # Convert input image to grayscale
    if len(image.shape) == 3:

        grayscale = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

    elif len(image.shape) == 2:

        grayscale = image.copy()

    else:

        raise ValueError(
            "Unsupported image dimensions."
        )

    # Detect four registration markers
    markers = detect_registration_markers(
        grayscale
    )

    # Correct page rotation and perspective
    aligned_image = correct_perspective(
        grayscale,
        markers
    )

    return aligned_image


# ==========================================
# 6. SAVE OUTPUT IMAGES
# ==========================================

def save_image(image, filename):

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = PROCESSED_DATA_DIR / filename

    success = cv2.imwrite(
        str(output_path),
        image
    )

    if not success:
        raise IOError(
            f"Could not save image: {output_path}"
        )

    print(f"Saved: {output_path}")


# ==========================================
# 7. MAIN FUNCTION
# ==========================================

def main():

    print("=" * 45)
    print(" SMARTOMR AI - REGISTRATION ALIGNMENT")
    print("=" * 45)

    print("\nLoading OMR grayscale image...")

    image = load_grayscale_image()

    print("Image loaded successfully!")

    # Detect four registration markers
    print("\nDetecting registration markers...")

    markers = detect_registration_markers(
        image
    )

    print("\nAll four registration markers detected!")

    # Save marker visualization
    marker_image = draw_registration_markers(
        image,
        markers
    )

    save_image(
        marker_image,
        "omr_registration_markers.png"
    )

    # Correct perspective
    print("\nApplying perspective correction...")

    aligned_image = correct_perspective(
        image,
        markers
    )

    save_image(
        aligned_image,
        "omr_aligned.png"
    )

    print("\nRegistration detection completed!")
    print("Perspective correction completed successfully!")


# ==========================================
# 8. EXECUTION
# ==========================================

if __name__ == "__main__":
    main()
