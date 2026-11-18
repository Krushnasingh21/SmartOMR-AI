
from datetime import datetime, timezone

from database.db import SessionLocal
from database.models import Exam, Student, OMRResult

def _to_json_safe(value):
    """Convert nested values into JSON-compatible Python values."""

    if isinstance(value, dict):
        return {
            str(key): _to_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [_to_json_safe(item) for item in value]

    if hasattr(value, "item"):
        return value.item()

    return value

def save_omr_result(
    exam_id,
    student_id,
    detected_answers,
    evaluation
):
    """
    Save a student's OMR result.
    Update the existing result if the student was already evaluated
    for the same exam.
    """

    db = SessionLocal()

    try:
        exam = db.query(Exam).filter(
            Exam.id == exam_id
        ).first()

        if not exam:
            raise ValueError("Examination not found.")

        student = db.query(Student).filter(
            Student.id == student_id
        ).first()

        if not student:
            raise ValueError("Student not found.")

        if not isinstance(detected_answers, dict):
            raise ValueError("Detected answers must be a dictionary.")

        if not isinstance(evaluation, dict):
            raise ValueError("Evaluation must be a dictionary.")

        result = db.query(OMRResult).filter(
            OMRResult.exam_id == exam_id,
            OMRResult.student_id == student_id
        ).first()

        if result is None:
            result = OMRResult(
                exam_id=exam_id,
                student_id=student_id
            )
            db.add(result)

        result.detected_answers = _to_json_safe(
            detected_answers
        )

        result.correct = int(evaluation.get("correct", 0))
        result.incorrect = int(evaluation.get("incorrect", 0))
        result.unanswered = int(evaluation.get("unanswered", 0))
        result.review_required = int(
            evaluation.get("review_required", 0)
        )

        result.score = float(evaluation.get("score", 0))
        result.maximum_marks = float(
            evaluation.get("maximum_marks", 0)
        )
        result.percentage = float(
            evaluation.get("percentage", 0)
        )

        result.evaluated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(result)

        return {
            "success": True,
            "message": "OMR result saved successfully.",
            "result_id": result.id
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

def get_all_results():
    """Retrieve all saved OMR results."""

    db = SessionLocal()

    try:
        results = (
            db.query(OMRResult)
            .order_by(OMRResult.evaluated_at.desc())
            .all()
        )

        return [
            {
                "result_id": result.id,
                "exam_id": result.exam_id,
                "student_id": result.student_id,
                "detected_answers": result.detected_answers,
                "correct": result.correct,
                "incorrect": result.incorrect,
                "unanswered": result.unanswered,
                "review_required": result.review_required,
                "score": result.score,
                "maximum_marks": result.maximum_marks,
                "percentage": result.percentage,
                "evaluated_at": result.evaluated_at
            }
            for result in results
        ]

    finally:
        db.close()

def get_results_by_exam(exam_id):
    """Retrieve all student results for a particular exam."""

    db = SessionLocal()

    try:
        results = (
            db.query(OMRResult)
            .filter(OMRResult.exam_id == exam_id)
            .order_by(OMRResult.score.desc())
            .all()
        )

        return [
            {
                "result_id": result.id,
                "exam_id": result.exam_id,
                "student_id": result.student_id,
                "student_name": result.student.student_name,
                "roll_number": result.student.roll_number,
                "correct": result.correct,
                "incorrect": result.incorrect,
                "unanswered": result.unanswered,
                "review_required": result.review_required,
                "score": result.score,
                "maximum_marks": result.maximum_marks,
                "percentage": result.percentage,
                "evaluated_at": result.evaluated_at
            }
            for result in results
        ]

    finally:
        db.close()

def get_all_results():

    db = SessionLocal()

    try:

        results = (
            db.query(OMRResult, Exam, Student)
            .join(Exam, OMRResult.exam_id == Exam.id)
            .join(Student, OMRResult.student_id == Student.id)
            .order_by(OMRResult.evaluated_at.desc())
            .all()
        )

        result_list = []

        for omr_result, exam, student in results:

            result_list.append({

                "result_id": omr_result.id,

                "exam_id": omr_result.exam_id,

                "exam_name": exam.exam_name,

                "student_id": omr_result.student_id,

                "student_name": student.student_name,

                "roll_number": student.roll_number,

                "detected_answers": omr_result.detected_answers,

                "correct": omr_result.correct,

                "incorrect": omr_result.incorrect,

                "unanswered": omr_result.unanswered,

                "review_required": omr_result.review_required,

                "score": omr_result.score,

                "maximum_marks": omr_result.maximum_marks,

                "percentage": omr_result.percentage,

                "evaluated_at": (
                    omr_result.evaluated_at.isoformat()
                    if omr_result.evaluated_at
                    else None
                )

            })

        return result_list

    except Exception as error:

        print(f"Error retrieving OMR results: {error}")

        return []

    finally:

        db.close()