
import cv2
import numpy as np

from config import PROCESSED_DATA_DIR


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

        # Calculate width-to-height ratio
        aspect_ratio = w / float(h)

        # Marker size and shape filtering
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

    print(f"Square marker candidates found: {len(candidates)}")

    # Divide the image into four corner regions
    corner_regions = {
        "top_left": (0, 0, width * 0.18, height * 0.12),
        "top_right": (width * 0.82, 0, width, height * 0.12),
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

    # Select the largest suitable square in each corner
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

    output = cv2.cvtColor(
        image,
        cv2.COLOR_GRAY2BGR
    )

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

    height, width = image.shape

    # Source points in clockwise order
    source_points = np.array([
        markers["top_left"],
        markers["top_right"],
        markers["bottom_right"],
        markers["bottom_left"]
    ], dtype=np.float32)

    # Target marker centers for the standard page
    margin_x = width * 0.037
    margin_y = height * 0.026

    destination_points = np.array([
        [margin_x, margin_y],
        [width - margin_x, margin_y],
        [width - margin_x, height - margin_y],
        [margin_x, height - margin_y]
    ], dtype=np.float32)

    # Calculate perspective transformation matrix
    matrix = cv2.getPerspectiveTransform(
        source_points,
        destination_points
    )

    # Apply transformation
    aligned_image = cv2.warpPerspective(
        image,
        matrix,
        (width, height)
    )

    return aligned_image


# ==========================================
# 5. SAVE OUTPUT IMAGES
# ==========================================

def save_image(image, filename):

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
# 6. MAIN FUNCTION
# ==========================================

def main():

    print("Loading OMR grayscale image...")

    image = load_grayscale_image()

    print("Image loaded successfully!")

    # Detect four registration markers
    print("\nDetecting registration markers...")

    markers = detect_registration_markers(image)

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
# 7. EXECUTION
# ==========================================

if __name__ == "__main__":
    main()
