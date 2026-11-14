
from src.answer_evaluator import evaluate_answers


def test_all_correct_answers():
    answer_key = {1: "A", 2: "B", 3: "C"}
    detected = {1: "A", 2: "B", 3: "C"}

    result = evaluate_answers(detected, answer_key)

    assert result["correct"] == 3
    assert result["incorrect"] == 0
    assert result["unanswered"] == 0
    assert result["score"] == 3


def test_incorrect_answers():
    answer_key = {1: "A", 2: "B", 3: "C"}
    detected = {1: "A", 2: "D", 3: "C"}

    result = evaluate_answers(detected, answer_key)

    assert result["correct"] == 2
    assert result["incorrect"] == 1
    assert result["score"] == 2


def test_unanswered_questions():
    answer_key = {1: "A", 2: "B", 3: "C"}
    detected = {1: "A"}

    result = evaluate_answers(detected, answer_key)

    assert result["correct"] == 1
    assert result["unanswered"] == 2
    assert result["score"] == 1


def test_multiple_marks():
    answer_key = {1: "A"}
    detected = {1: "MULTIPLE_MARKS"}

    result = evaluate_answers(detected, answer_key)

    assert result["incorrect"] == 1
    assert result["score"] == 0


def test_review_required():
    answer_key = {1: "A"}
    detected = {1: "REVIEW_REQUIRED"}

    result = evaluate_answers(detected, answer_key)

    assert result["review_required"] == 1
    assert result["correct"] == 0
    assert result["incorrect"] == 0


def test_percentage_calculation():
    answer_key = {1: "A", 2: "B", 3: "C", 4: "D"}
    detected = {1: "A", 2: "B", 3: "A", 4: "D"}

    result = evaluate_answers(detected, answer_key)

    assert result["score"] == 3
    assert result["percentage"] == 75.0
