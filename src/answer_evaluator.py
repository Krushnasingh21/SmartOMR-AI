
# ==========================================
# SMARTOMR AI - ANSWER EVALUATOR
# ==========================================


def evaluate_answers(
    detected_answers,
    answer_key,
    marks_per_correct=1,
    marks_per_wrong=0,
    negative_marking=0
):
    """
    Compare detected answers with the answer key.

    Parameters:
        detected_answers: Dictionary of extracted answers.
        answer_key: Dictionary containing correct answers.
        marks_per_correct: Marks for each correct answer.
        marks_per_wrong: Retained for compatibility.
        negative_marking: Marks deducted for each incorrect answer.

    Returns:
        Dictionary containing evaluation statistics.
    """

    if not isinstance(detected_answers, dict):
        raise TypeError(
            "Detected answers must be a dictionary."
        )

    if not isinstance(answer_key, dict) or not answer_key:
        raise ValueError(
            "Answer key must be a non-empty dictionary."
        )

    if marks_per_correct < 0 or negative_marking < 0:
        raise ValueError(
            "Marking values cannot be negative."
        )

    correct = 0
    incorrect = 0
    unanswered = 0
    review_required = 0

    for question, correct_answer in answer_key.items():

        # Convert question number to integer
        question = int(question)

        # Get detected answer
        detected = detected_answers.get(
            question,
            "UNANSWERED"
        )

        # Handle uncertain answers
        if detected in (
            "REVIEW_REQUIRED",
            "MULTIPLE_MARKS"
        ):

            review_required += 1

        # Handle unanswered questions
        elif detected == "UNANSWERED":

            unanswered += 1

        # Handle correct answers
        elif detected == correct_answer:

            correct += 1

        # Handle incorrect answers
        else:

            incorrect += 1

    total_questions = len(answer_key)

    # Calculate final score
    score = (
        correct * marks_per_correct
        - incorrect * negative_marking
    )

    maximum_marks = (
        total_questions * marks_per_correct
    )

    # Calculate percentage
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
