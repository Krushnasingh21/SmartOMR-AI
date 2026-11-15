
from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.models import Exam


# ==========================================
# 1. CREATE EXAM
# ==========================================

def create_exam(
    exam_name,
    total_questions,
    options_per_question=4,
    marks_per_correct=1.0,
    negative_marking=0.0
):
    """
    Create and save a new examination.
    """

    db: Session = SessionLocal()

    try:
        if not exam_name or not exam_name.strip():
            raise ValueError("Exam name cannot be empty.")

        if total_questions <= 0:
            raise ValueError("Total questions must be greater than zero.")

        if options_per_question < 2:
            raise ValueError("At least two options are required.")

        if marks_per_correct <= 0:
            raise ValueError("Marks per correct answer must be positive.")

        if negative_marking < 0:
            raise ValueError("Negative marking cannot be negative.")

        new_exam = Exam(
            exam_name=exam_name.strip(),
            total_questions=total_questions,
            options_per_question=options_per_question,
            marks_per_correct=marks_per_correct,
            negative_marking=negative_marking
        )

        db.add(new_exam)
        db.commit()
        db.refresh(new_exam)

        return {
            "success": True,
            "exam_id": new_exam.id,
            "exam_name": new_exam.exam_name,
            "message": "Exam created successfully."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ==========================================
# 2. READ / GET ALL EXAMS
# ==========================================

def get_all_exams():
    """
    Retrieve all examinations from the database.
    """

    db = SessionLocal()

    try:
        exams = db.query(Exam).order_by(Exam.id.asc()).all()

        exam_list = []

        for exam in exams:
            exam_data = {
                "exam_id": exam.id,
                "exam_name": exam.exam_name,
                "total_questions": exam.total_questions,
                "options_per_question": exam.options_per_question,
                "marks_per_correct": exam.marks_per_correct,
                "negative_marking": exam.negative_marking,
                "created_at": exam.created_at
            }

            exam_list.append(exam_data)

        return exam_list

    finally:
        db.close()


# ==========================================
# 3. UPDATE EXAM
# ==========================================

def update_exam(
    exam_id,
    exam_name=None,
    total_questions=None,
    options_per_question=None,
    marks_per_correct=None,
    negative_marking=None
):
    """
    Update an existing examination.
    """

    db = SessionLocal()

    try:
        exam = db.query(Exam).filter(
            Exam.id == exam_id
        ).first()

        if exam is None:
            raise ValueError(f"Exam with ID {exam_id} not found.")

        if exam_name is not None:
            if not exam_name.strip():
                raise ValueError("Exam name cannot be empty.")
            exam.exam_name = exam_name.strip()

        if total_questions is not None:
            if total_questions <= 0:
                raise ValueError("Total questions must be greater than zero.")
            exam.total_questions = total_questions

        if options_per_question is not None:
            if options_per_question < 2:
                raise ValueError("At least two options are required.")
            exam.options_per_question = options_per_question

        if marks_per_correct is not None:
            if marks_per_correct <= 0:
                raise ValueError("Marks per correct answer must be positive.")
            exam.marks_per_correct = marks_per_correct

        if negative_marking is not None:
            if negative_marking < 0:
                raise ValueError("Negative marking cannot be negative.")
            exam.negative_marking = negative_marking

        db.commit()
        db.refresh(exam)

        return {
            "success": True,
            "exam_id": exam.id,
            "exam_name": exam.exam_name,
            "message": "Exam updated successfully."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ==========================================
# 4. DELETE EXAM
# ==========================================

def delete_exam(exam_id):
    """
    Delete an existing examination.
    """

    db = SessionLocal()

    try:
        exam = db.query(Exam).filter(
            Exam.id == exam_id
        ).first()

        if exam is None:
            raise ValueError(f"Exam with ID {exam_id} not found.")

        exam_name = exam.exam_name

        db.delete(exam)
        db.commit()

        return {
            "success": True,
            "exam_id": exam_id,
            "exam_name": exam_name,
            "message": "Exam deleted successfully."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ==========================================
# 5. TEST ALL CRUD OPERATIONS
# ==========================================

if __name__ == "__main__":

    print("\n===== CREATE EXAM TEST =====")

    result = create_exam(
        exam_name="Temporary CRUD Test",
        total_questions=100,
        options_per_question=4,
        marks_per_correct=1,
        negative_marking=0.25
    )

    test_exam_id = result["exam_id"]

    print("Success:", result["success"])
    print("Exam ID:", test_exam_id)
    print("Exam Name:", result["exam_name"])

    # --------------------------------------

    print("\n===== GET ALL EXAMS TEST =====")

    all_exams = get_all_exams()

    print("Total Exams:", len(all_exams))

    for exam in all_exams:
        print(exam)

    # --------------------------------------

    print("\n===== UPDATE EXAM TEST =====")

    update_result = update_exam(
        exam_id=test_exam_id,
        exam_name="Updated Temporary CRUD Test",
        marks_per_correct=2,
        negative_marking=0.5
    )

    print("Update Result:", update_result)

    # --------------------------------------

    print("\n===== DELETE EXAM TEST =====")

    delete_result = delete_exam(test_exam_id)

    print("Delete Result:", delete_result)

    # --------------------------------------

    print("\n===== VERIFY DELETION =====")

    remaining_exams = get_all_exams()

    print("Remaining Exams:", len(remaining_exams))

    deleted_exam_exists = any(
        exam["exam_id"] == test_exam_id
        for exam in remaining_exams
    )

    print("Deleted Exam Still Exists:", deleted_exam_exists)

    print("\nAll CRUD tests completed successfully!")
