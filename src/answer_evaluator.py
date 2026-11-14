from src.bubble_detection import (
    load_omr_image,
    detect_all_answers
)

def evaluate_answers(
    detected_answers,
    answer_key,
    marks_per_correct=1,
    marks_per_wrong=0,
    negative_marking=0
):
    """
    Compare detected answers with the answer key
    and calculate the student's result.
    """

    correct = 0
    incorrect = 0
    unanswered = 0
    review_required = 0

    for question, correct_answer in answer_key.items():

        detected = detected_answers.get(
            question, "UNANSWERED"
        )

        if detected == "REVIEW_REQUIRED":
            review_required += 1

        elif detected == "UNANSWERED":
            unanswered += 1

        elif detected == correct_answer:
            correct += 1

        else:
            incorrect += 1

    total_questions = len(answer_key)

    score = (
        correct * marks_per_correct
        - incorrect * negative_marking
    )

    maximum_marks = total_questions * marks_per_correct

    percentage = (
        (score / maximum_marks) * 100
        if maximum_marks > 0 else 0
    )

    return {
        "total_questions": total_questions,
        "correct": correct,
        "incorrect": incorrect,
        "unanswered": unanswered,
        "review_required": review_required,
        "score": round(score, 2),
        "maximum_marks": round(maximum_marks, 2),
        "percentage": round(percentage, 2)
    }




if __name__ == "__main__":

    # Step 1: Load OMR image
    print("Loading OMR sheet...")

    image = load_omr_image()

    # Step 2: Detect all answers automatically
    print("Detecting answers...")

    detection_results = detect_all_answers(image)

    # Extract only the detected answer values
    detected_answers = {
        question: details["answer"]
        for question, details in detection_results.items()
    }

    # Step 3: Define answer key
    answer_key = {
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

    # Placeholder answer key for remaining questions
    for question in range(11, 101):
        answer_key[question] = "A"

    # Step 4: Evaluate answers
    print("Evaluating answers...")

    result = evaluate_answers(
        detected_answers,
        answer_key,
        marks_per_correct=1,
        marks_per_wrong=0,
        negative_marking=0
    )

    # Step 5: Display result
    print("\n===== SMARTOMR AI FINAL RESULT =====")

    print(f"Total Questions: {result['total_questions']}")
    print(f"Correct Answers: {result['correct']}")
    print(f"Incorrect Answers: {result['incorrect']}")
    print(f"Unanswered: {result['unanswered']}")
    print(f"Review Required: {result['review_required']}")

    print("-----------------------------------")

    print(
        f"Final Score: "
        f"{result['score']}/{result['maximum_marks']}"
    )

    print(f"Percentage: {result['percentage']}%")

    print("\nEvaluation completed!")