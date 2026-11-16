
import cv2
import numpy as np
import pymupdf

from pathlib import Path

from src.layout_detector import detect_layout
from src.registration_alignment import align_omr_image
from src.omr_structure_detector import detect_omr_structure
from src.bubble_detection import detect_all_answers
from src.answer_evaluator import evaluate_answers


# ==========================================
# SMARTOMR AI - CENTRAL OMR PROCESSING PIPELINE
# ==========================================

SUPPORTED_IMAGE_FORMATS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp"
}

SUPPORTED_FORMATS = SUPPORTED_IMAGE_FORMATS | {".pdf"}


# ==========================================
# 1. LOAD AND VALIDATE OMR INPUT
# ==========================================

def load_input_image(input_source):
    """
    Load an OMR image from:
    1. Image file path
    2. PDF file path (first page)
    3. OpenCV NumPy image (camera/upload)

    Returns a BGR image.
    """

    # Case 1: Image already provided as NumPy array
    if isinstance(input_source, np.ndarray):

        if input_source.size == 0:
            raise ValueError("Input image is empty.")

        image = input_source.copy()

        if len(image.shape) == 2:
            image = cv2.cvtColor(
                image,
                cv2.COLOR_GRAY2BGR
            )

        elif len(image.shape) == 3:

            if image.shape[2] == 4:
                image = cv2.cvtColor(
                    image,
                    cv2.COLOR_BGRA2BGR
                )

            elif image.shape[2] != 3:
                raise ValueError(
                    "Unsupported image channel count."
                )

        else:
            raise ValueError(
                "Unsupported image dimensions."
            )

        return image

    # Case 2: File path
    if isinstance(input_source, (str, Path)):

        file_path = Path(input_source)

        if not file_path.exists():
            raise FileNotFoundError(
                f"OMR file not found: {file_path}"
            )

        extension = file_path.suffix.lower()

        if extension not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file format: {extension}"
            )

        # Load PDF
        if extension == ".pdf":

            document = pymupdf.open(str(file_path))

            try:
                if len(document) == 0:
                    raise ValueError("PDF contains no pages.")

                page = document[0]

                pix = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False
                )

                image = np.frombuffer(
                    pix.samples,
                    dtype=np.uint8
                ).reshape(
                    pix.height,
                    pix.width,
                    pix.n
                )

                image = cv2.cvtColor(
                    image,
                    cv2.COLOR_RGB2BGR
                )

            finally:
                document.close()

            return image

        # Load regular image
        image = cv2.imread(
            str(file_path),
            cv2.IMREAD_COLOR
        )

        if image is None:
            raise ValueError(
                f"Unable to read image: {file_path}"
            )

        return image

    raise TypeError(
        "Input must be an image path, PDF path, or NumPy image."
    )


# ==========================================
# 2. DETECT OMR LAYOUT
# ==========================================

def validate_omr_layout(image):
    """
    Identify whether the uploaded sheet matches
    the supported SmartOMR standard layout.
    """

    print("\n[STEP 1] Detecting OMR layout...")

    layout_result = detect_layout(image)

    print(
        "Detected layout:",
        layout_result["layout_name"]
    )

    print(
        "Layout confidence:",
        layout_result["confidence"]
    )

    print(
        "Registration markers:",
        layout_result["marker_count"]
    )

    if layout_result["requires_calibration"]:

        raise ValueError(
            "Unknown OMR layout. "
            + layout_result["message"]
        )

    if layout_result["layout_id"] != "smartomr_standard_100":

        raise ValueError(
            "The uploaded sheet does not match "
            "the supported standard layout."
        )

    return layout_result


# ==========================================
# 3. ALIGN OMR IMAGE
# ==========================================

def align_input_image(image):
    """
    Detect registration markers and correct
    image rotation and perspective.
    """

    print("\n[STEP 2] Aligning OMR image...")

    aligned_gray = align_omr_image(image)

    # Structure and bubble detectors expect BGR
    aligned_bgr = cv2.cvtColor(
        aligned_gray,
        cv2.COLOR_GRAY2BGR
    )

    print("Image alignment completed.")

    return aligned_bgr


# ==========================================
# 4. DETECT OMR STRUCTURE
# ==========================================

def validate_omr_structure(image):
    """
    Validate the expected 100-question,
    two-column, four-option OMR structure.
    """

    print("\n[STEP 3] Detecting OMR structure...")

    structure_result = detect_omr_structure(
        image,
        expected_options=4
    )

    if structure_result["layout_id"] != "smartomr_standard_100":

        raise ValueError(
            "OMR structure validation failed. "
            + structure_result["message"]
        )

    print(
        "Total questions:",
        structure_result["total_questions"]
    )

    print(
        "Expected bubble positions:",
        structure_result["expected_bubble_positions"]
    )

    print(
        "Detected bubble positions:",
        structure_result["detected_bubble_positions"]
    )

    print(
        "Complete question groups:",
        structure_result["detected_question_groups"]
    )

    return structure_result


# ==========================================
# 5. DETECT ANSWERS
# ==========================================

def extract_omr_answers(image):
    """
    Detect bubbles and extract answers
    for all 100 questions.
    """

    print("\n[STEP 4] Detecting bubbles and answers...")

    detection_results = detect_all_answers(image)

    detected_answers = {
        question: details["answer"]
        for question, details in detection_results.items()
    }

    answered = sum(
        1 for answer in detected_answers.values()
        if answer not in (
            "UNANSWERED",
            "REVIEW_REQUIRED",
            "MULTIPLE_MARKS"
        )
    )

    unanswered = sum(
        1 for answer in detected_answers.values()
        if answer == "UNANSWERED"
    )

    review_required = sum(
        1 for answer in detected_answers.values()
        if answer in (
            "REVIEW_REQUIRED",
            "MULTIPLE_MARKS"
        )
    )

    print("Total questions:", len(detected_answers))
    print("Answered:", answered)
    print("Unanswered:", unanswered)
    print("Review required:", review_required)

    return detection_results, detected_answers


# ==========================================
# 6. EVALUATE ANSWERS
# ==========================================

def evaluate_omr_result(
    detected_answers,
    answer_key,
    marks_per_correct=1,
    marks_per_wrong=0,
    negative_marking=0
):
    """
    Compare extracted answers with the supplied
    answer key and calculate the final result.
    """

    print("\n[STEP 5] Evaluating answers...")

    if not isinstance(answer_key, dict) or not answer_key:
        raise ValueError(
            "A valid, non-empty answer key is required."
        )

    normalized_key = {}

    for question, answer in answer_key.items():

        try:
            question_number = int(question)
        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid answer-key question number: {question}"
            )

        if question_number not in detected_answers:
            raise ValueError(
                f"Question {question_number} is outside "
                "the detected OMR question range."
            )

        if answer not in ("A", "B", "C", "D"):
            raise ValueError(
                f"Invalid answer-key option for question "
                f"{question_number}: {answer}"
            )

        normalized_key[question_number] = answer

    result = evaluate_answers(
        detected_answers,
        normalized_key,
        marks_per_correct=marks_per_correct,
        marks_per_wrong=marks_per_wrong,
        negative_marking=negative_marking
    )

    print("\nEvaluation completed.")

    return result


# ==========================================
# 7. MAIN PIPELINE FUNCTION
# ==========================================

def process_omr(
    input_source,
    answer_key=None,
    marks_per_correct=1,
    marks_per_wrong=0,
    negative_marking=0
):
    """
    Execute the complete SmartOMR AI pipeline.

    Parameters:
        input_source:
            Image path, PDF path, or NumPy image.

        answer_key:
            Optional dictionary containing question
            numbers and correct options.

        marks_per_correct:
            Marks awarded for each correct answer.

        marks_per_wrong:
            Retained for compatibility with evaluator.

        negative_marking:
            Marks deducted for incorrect answers.

    Returns:
        Dictionary containing layout, structure,
        detection results, answers and evaluation.
    """

    print("\n" + "=" * 55)
    print("          SMARTOMR AI - OMR PIPELINE")
    print("=" * 55)

    # STEP 1: Load image
    print("\nLoading OMR input...")

    original_image = load_input_image(input_source)

    print(
        "Image dimensions:",
        original_image.shape
    )

    # STEP 2: Detect layout
    layout_result = validate_omr_layout(
        original_image
    )

    # STEP 3: Align image
    aligned_image = align_input_image(
        original_image
    )

    # STEP 4: Detect structure
    structure_result = validate_omr_structure(
        aligned_image
    )

    # STEP 5: Detect answers
    detection_results, detected_answers = extract_omr_answers(
        aligned_image
    )

    # STEP 6: Evaluate if answer key is provided
    evaluation_result = None

    if answer_key is not None:

        evaluation_result = evaluate_omr_result(
            detected_answers,
            answer_key,
            marks_per_correct=marks_per_correct,
            marks_per_wrong=marks_per_wrong,
            negative_marking=negative_marking
        )

    # Final pipeline output
    pipeline_result = {

        "success": True,

        "layout": layout_result,

        "structure": structure_result,

        "detection_results": detection_results,

        "detected_answers": detected_answers,

        "evaluation": evaluation_result,

        "aligned_image": aligned_image

    }

    print("\n" + "=" * 55)
    print("       SMARTOMR AI PIPELINE COMPLETED")
    print("=" * 55)

    if evaluation_result is not None:

        print(
            "Final Score:",
            f"{evaluation_result['score']}/"
            f"{evaluation_result['maximum_marks']}"
        )

        print(
            "Percentage:",
            f"{evaluation_result['percentage']}%"
        )

    return pipeline_result


# ==========================================
# 8. MODULE EXECUTION
# ==========================================

if __name__ == "__main__":

    print("SmartOMR AI pipeline module loaded.")
    print("Ready to process OMR images and PDFs.")

    print("\nSupported input formats:")
    print("JPG, JPEG, PNG, BMP, PDF")

    print("\nPipeline functions:")
    print("1. load_input_image()")
    print("2. validate_omr_layout()")
    print("3. align_input_image()")
    print("4. validate_omr_structure()")
    print("5. extract_omr_answers()")
    print("6. evaluate_omr_result()")
    print("7. process_omr()")
