
from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.models import Exam, AnswerKey


# ==========================================
# 1. VALIDATE ANSWER KEY
# ==========================================

def validate_answer_key(answers, total_questions, options_per_question):
    """
    Validate answers against examination settings.
    """

    if not isinstance(answers, dict):
        raise ValueError("Answers must be provided as a dictionary.")

    if total_questions < 1:
        raise ValueError("Total questions must be greater than zero.")

    if options_per_question not in [2, 3, 4, 5]:
        raise ValueError("Invalid number of options.")

    allowed_options = ["A", "B", "C", "D", "E"][
        :options_per_question
    ]

    validated_answers = {}

    for question_number, answer in answers.items():

        try:
            question_number = int(question_number)
        except (ValueError, TypeError):
            raise ValueError(
                f"Invalid question number: {question_number}"
            )

        if question_number in validated_answers:
            raise ValueError(
                f"Duplicate question number: {question_number}"
            )

        if not 1 <= question_number <= total_questions:
            raise ValueError(
                f"Question number {question_number} is out of range."
            )

        if not isinstance(answer, str):
            raise ValueError(
                f"Invalid answer for question {question_number}."
            )

        answer = answer.strip().upper()

        if answer not in allowed_options:
            raise ValueError(
                f"Invalid option '{answer}' for question "
                f"{question_number}. Allowed options: {allowed_options}"
            )

        validated_answers[question_number] = answer

    expected_questions = set(range(1, total_questions + 1))
    provided_questions = set(validated_answers.keys())

    missing_questions = expected_questions - provided_questions

    if missing_questions:
        raise ValueError(
            f"Missing answers for questions: "
            f"{sorted(missing_questions)}"
        )

    return {
        str(question): answer
        for question, answer in sorted(validated_answers.items())
    }


# ==========================================
# 2. CREATE ANSWER KEY
# ==========================================

def create_answer_key(exam_id, answers):
    """
    Create and save an answer key for an examination.
    """

    db: Session = SessionLocal()

    try:

        exam = db.query(Exam).filter(
            Exam.id == exam_id
        ).first()

        if exam is None:
            raise ValueError(
                f"Examination with ID {exam_id} not found."
            )

        existing_key = db.query(AnswerKey).filter(
            AnswerKey.exam_id == exam_id
        ).first()

        if existing_key:
            raise ValueError(
                "An answer key already exists for this examination."
            )

        validated_answers = validate_answer_key(
            answers=answers,
            total_questions=exam.total_questions,
            options_per_question=exam.options_per_question
        )

        new_answer_key = AnswerKey(
            exam_id=exam_id,
            answers=validated_answers
        )

        db.add(new_answer_key)
        db.commit()
        db.refresh(new_answer_key)

        return {
            "success": True,
            "answer_key_id": new_answer_key.id,
            "exam_id": new_answer_key.exam_id,
            "answers": new_answer_key.answers,
            "message": "Answer key created successfully."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ==========================================
# 3. GET ANSWER KEY FOR AN EXAM
# ==========================================

def get_answer_key(exam_id):
    """
    Retrieve the answer key associated with an examination.
    """

    db = SessionLocal()

    try:

        answer_key = db.query(AnswerKey).filter(
            AnswerKey.exam_id == exam_id
        ).first()

        if answer_key is None:
            return None

        return {
            "answer_key_id": answer_key.id,
            "exam_id": answer_key.exam_id,
            "answers": {
                int(question): answer
                for question, answer in answer_key.answers.items()
            }
        }

    finally:
        db.close()


# ==========================================
# 4. GET ALL ANSWER KEYS
# ==========================================

def get_all_answer_keys():
    """
    Retrieve all saved answer keys with examination details.
    """

    db = SessionLocal()

    try:

        records = db.query(
            AnswerKey,
            Exam.exam_name
        ).join(
            Exam,
            AnswerKey.exam_id == Exam.id
        ).order_by(
            AnswerKey.id.asc()
        ).all()

        answer_key_list = []

        for answer_key, exam_name in records:

            answer_key_list.append({
                "answer_key_id": answer_key.id,
                "exam_id": answer_key.exam_id,
                "exam_name": exam_name,
                "total_questions": len(answer_key.answers),
                "answers": {
                    int(question): answer
                    for question, answer in answer_key.answers.items()
                }
            })

        return answer_key_list

    finally:
        db.close()


# ==========================================
# 5. UPDATE ANSWER KEY
# ==========================================

def update_answer_key(exam_id, updated_answers):
    """
    Update an existing examination's answer key.
    """

    db = SessionLocal()

    try:

        answer_key = db.query(AnswerKey).filter(
            AnswerKey.exam_id == exam_id
        ).first()

        if answer_key is None:
            raise ValueError(
                f"Answer key for examination ID {exam_id} not found."
            )

        exam = db.query(Exam).filter(
            Exam.id == exam_id
        ).first()

        if exam is None:
            raise ValueError(
                f"Examination with ID {exam_id} not found."
            )

        validated_answers = validate_answer_key(
            answers=updated_answers,
            total_questions=exam.total_questions,
            options_per_question=exam.options_per_question
        )

        answer_key.answers = validated_answers

        db.commit()
        db.refresh(answer_key)

        return {
            "success": True,
            "answer_key_id": answer_key.id,
            "exam_id": answer_key.exam_id,
            "answers": answer_key.answers,
            "message": "Answer key updated successfully."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ==========================================
# 6. DELETE ANSWER KEY
# ==========================================

def delete_answer_key(exam_id):
    """
    Delete the answer key associated with an examination.
    """

    db = SessionLocal()

    try:

        answer_key = db.query(AnswerKey).filter(
            AnswerKey.exam_id == exam_id
        ).first()

        if answer_key is None:
            raise ValueError(
                f"Answer key for examination ID {exam_id} not found."
            )

        answer_key_id = answer_key.id

        db.delete(answer_key)
        db.commit()

        return {
            "success": True,
            "answer_key_id": answer_key_id,
            "exam_id": exam_id,
            "message": "Answer key deleted successfully."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
