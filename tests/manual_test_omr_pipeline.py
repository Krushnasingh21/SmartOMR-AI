
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.omr_pipeline import process_omr


PROJECT_DIR = Path(__file__).resolve().parents[1]

PDF_PATH = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "standard_100_question_omr_filled.pdf"
)

ANSWER_KEY = {
    1: "A",
    2: "C",
    3: "B",
    4: "D",
    5: "A",
    6: "B",
    7: "C",
    8: "D",
    9: "A",
    10: "C"
}

# Placeholder answers for questions 11-100.
# Replace these with the actual exam answer key
# before using this result for a real evaluation.
for question in range(11, 101):
    ANSWER_KEY[question] = "A"


def main():

    print("=" * 50)
    print(" SMARTOMR AI - COMPLETE PIPELINE TEST")
    print("=" * 50)

    result = process_omr(
        input_source=PDF_PATH,
        answer_key=ANSWER_KEY,
        marks_per_correct=1,
        marks_per_wrong=0,
        negative_marking=0
    )

    print("\nFINAL PIPELINE VERIFICATION")
    print("-" * 50)

    print("Pipeline success:", result["success"])

    print(
        "Layout:",
        result["layout"]["layout_id"]
    )

    print(
        "Detected questions:",
        len(result["detected_answers"])
    )

    print(
        "Complete question groups:",
        result["structure"]["detected_question_groups"]
    )

    print("\nEVALUATION RESULT")

    evaluation = result["evaluation"]

    for key, value in evaluation.items():
        print(f"{key}: {value}")

    print("\nSUCCESS: Pipeline test completed!")


if __name__ == "__main__":
    main()
