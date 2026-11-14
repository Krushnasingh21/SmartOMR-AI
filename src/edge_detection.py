
import cv2

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
            f"Grayscale image not found: {input_path}"
        )

    return image


# ==========================================
# 2. CANNY EDGE DETECTION
# ==========================================

def apply_canny(image):

    edges = cv2.Canny(
        image,
        threshold1=50,
        threshold2=150
    )

    return edges


# ==========================================
# 3. DILATION
# ==========================================

def apply_dilation(edges):

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (3, 3)
    )

    dilated = cv2.dilate(
        edges,
        kernel,
        iterations=1
    )

    return dilated


# ==========================================
# 4. SAVE PROCESSED IMAGE
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
# 5. MAIN FUNCTION
# ==========================================

def main():

    print("Loading grayscale OMR image...")

    grayscale = load_grayscale_image()

    print("Grayscale image loaded successfully!")

    # Apply Canny edge detection
    edges = apply_canny(grayscale)

    print("Canny edge detection completed!")

    # Apply dilation
    dilated_edges = apply_dilation(edges)

    print("Dilation completed!")

    # Save output images
    save_image(
        edges,
        "omr_edges.png"
    )

    save_image(
        dilated_edges,
        "omr_dilated_edges.png"
    )

    print("\nEdge detection process completed successfully!")


# ==========================================
# 6. EXECUTION
# ==========================================

if __name__ == "__main__":
    main()
