
import cv2

from config import PROCESSED_DATA_DIR


# ==========================================
# 1. LOAD EDGE IMAGE
# ==========================================

def load_edge_image():

    input_path = PROCESSED_DATA_DIR / "omr_edges.png"

    image = cv2.imread(
        str(input_path),
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise FileNotFoundError(
            f"Edge image not found: {input_path}"
        )

    return image


# ==========================================
# 2. FIND CONTOURS
# ==========================================

def find_image_contours(image):

    contours, hierarchy = cv2.findContours(
        image.copy(),
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    print(f"Total contours detected: {len(contours)}")

    return contours, hierarchy


# ==========================================
# 3. FILTER CONTOURS BY AREA
# ==========================================

def filter_contours(contours, minimum_area=20):

    filtered_contours = []

    for contour in contours:

        area = cv2.contourArea(contour)

        if area >= minimum_area:
            filtered_contours.append(contour)

    print(
        f"Contours after filtering: {len(filtered_contours)}"
    )

    return filtered_contours


# ==========================================
# 4. DRAW CONTOURS
# ==========================================

def draw_detected_contours(image, contours):

    output = cv2.cvtColor(
        image,
        cv2.COLOR_GRAY2BGR
    )

    cv2.drawContours(
        output,
        contours,
        -1,
        (0, 255, 0),
        1
    )

    return output


# ==========================================
# 5. DRAW CONTOUR BOUNDING BOXES
# ==========================================

def draw_bounding_boxes(image, contours):

    output = image.copy()

    for contour in contours:

        x, y, width, height = cv2.boundingRect(contour)

        cv2.rectangle(
            output,
            (x, y),
            (x + width, y + height),
            (0, 0, 255),
            1
        )

    return output


# ==========================================
# 6. SAVE OUTPUT IMAGES
# ==========================================

def save_image(image, filename):

    output_path = PROCESSED_DATA_DIR / filename

    success = cv2.imwrite(
        str(output_path),
        image
    )

    if not success:
        raise IOError(f"Could not save image: {output_path}")

    print(f"Saved: {output_path}")


# ==========================================
# 7. MAIN FUNCTION
# ==========================================

def main():

    print("Loading OMR edge image...")

    edge_image = load_edge_image()

    print("Edge image loaded successfully!")

    # Find contours
    contours, hierarchy = find_image_contours(edge_image)

    # Filter small contours
    filtered_contours = filter_contours(
        contours,
        minimum_area=20
    )

    # Draw contours
    contour_image = draw_detected_contours(
        edge_image,
        filtered_contours
    )

    # Draw bounding boxes
    bounding_box_image = draw_bounding_boxes(
        contour_image,
        filtered_contours
    )

    # Save results
    save_image(
        contour_image,
        "omr_contours.png"
    )

    save_image(
        bounding_box_image,
        "omr_bounding_boxes.png"
    )

    print("\nContour detection completed successfully!")


# ==========================================
# 8. EXECUTION
# ==========================================

if __name__ == "__main__":
    main()
