
from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.models import Student


# ==========================================
# 1. CREATE / REGISTER STUDENT
# ==========================================

def create_student(student_name, roll_number, email=None):
    """
    Register a new student in the database.
    """

    db: Session = SessionLocal()

    try:
        # Validate student name
        if not student_name or not student_name.strip():
            raise ValueError("Student name cannot be empty.")

        # Validate roll number
        if not roll_number or not roll_number.strip():
            raise ValueError("Roll number cannot be empty.")

        student_name = student_name.strip()
        roll_number = roll_number.strip()

        # Check duplicate roll number
        existing_student = db.query(Student).filter(
            Student.roll_number == roll_number
        ).first()

        if existing_student:
            raise ValueError(
                f"Roll number {roll_number} is already registered."
            )

        # Create student object
        new_student = Student(
            student_name=student_name,
            roll_number=roll_number,
            email=email.strip() if email else None
        )

        # Save to database
        db.add(new_student)
        db.commit()
        db.refresh(new_student)

        return {
            "success": True,
            "student_id": new_student.id,
            "student_name": new_student.student_name,
            "roll_number": new_student.roll_number,
            "message": "Student registered successfully."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ==========================================
# 2. GET ALL REGISTERED STUDENTS
# ==========================================

def get_all_students():
    """
    Retrieve all registered students from the database.
    """

    db = SessionLocal()

    try:
        students = db.query(Student).order_by(
            Student.id.asc()
        ).all()

        student_list = []

        for student in students:
            student_data = {
                "student_id": student.id,
                "student_name": student.student_name,
                "roll_number": student.roll_number,
                "email": student.email
            }

            student_list.append(student_data)

        return student_list

    finally:
        db.close()


# ==========================================
# 3. SEARCH STUDENTS
# ==========================================

def search_students(search_query):
    """
    Search students by name or roll number.
    """

    db = SessionLocal()

    try:
        if not search_query or not search_query.strip():
            return []

        search_query = search_query.strip()

        students = db.query(Student).filter(
            (Student.student_name.ilike(f"%{search_query}%")) |
            (Student.roll_number.ilike(f"%{search_query}%"))
        ).order_by(Student.id.asc()).all()

        student_list = []

        for student in students:
            student_data = {
                "student_id": student.id,
                "student_name": student.student_name,
                "roll_number": student.roll_number,
                "email": student.email
            }

            student_list.append(student_data)

        return student_list

    finally:
        db.close()


# ==========================================
# 4. UPDATE STUDENT
# ==========================================

def update_student(
    student_id,
    student_name=None,
    roll_number=None,
    email=None
):
    """
    Update an existing student's information.
    """

    db = SessionLocal()

    try:
        # Find student by ID
        student = db.query(Student).filter(
            Student.id == student_id
        ).first()

        if student is None:
            raise ValueError(
                f"Student with ID {student_id} not found."
            )

        # Update student name
        if student_name is not None:
            if not student_name.strip():
                raise ValueError("Student name cannot be empty.")

            student.student_name = student_name.strip()

        # Update roll number
        if roll_number is not None:
            if not roll_number.strip():
                raise ValueError("Roll number cannot be empty.")

            roll_number = roll_number.strip()

            existing_student = db.query(Student).filter(
                Student.roll_number == roll_number,
                Student.id != student_id
            ).first()

            if existing_student:
                raise ValueError(
                    f"Roll number {roll_number} is already registered."
                )

            student.roll_number = roll_number

        # Update email
        if email is not None:
            student.email = email.strip() or None

        db.commit()
        db.refresh(student)

        return {
            "success": True,
            "student_id": student.id,
            "student_name": student.student_name,
            "roll_number": student.roll_number,
            "email": student.email,
            "message": "Student updated successfully."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ==========================================
# 5. DELETE STUDENT
# ==========================================

def delete_student(student_id):
    """
    Delete an existing student from the database.
    """

    db = SessionLocal()

    try:
        student = db.query(Student).filter(
            Student.id == student_id
        ).first()

        if student is None:
            raise ValueError(
                f"Student with ID {student_id} not found."
            )

        student_name = student.student_name
        roll_number = student.roll_number

        db.delete(student)
        db.commit()

        return {
            "success": True,
            "student_id": student_id,
            "student_name": student_name,
            "roll_number": roll_number,
            "message": "Student deleted successfully."
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ==========================================
# 2. TEST STUDENT REGISTRATION
# ==========================================


if __name__ == "__main__":

    print("\n===== GET ALL STUDENTS TEST =====")

    all_students = get_all_students()

    print("Total Registered Students:", len(all_students))

    for student in all_students:
        print("\nStudent ID:", student["student_id"])
        print("Student Name:", student["student_name"])
        print("Roll Number:", student["roll_number"])
        print("Email:", student["email"])

    print("\nStudent retrieval completed!")


if __name__ == "__main__":

    print("\n===== SEARCH STUDENTS TEST =====")

    search_query = "Rahul"

    results = search_students(search_query)

    print("Search Query:", search_query)
    print("Students Found:", len(results))

    for student in results:
        print("\nStudent ID:", student["student_id"])
        print("Student Name:", student["student_name"])
        print("Roll Number:", student["roll_number"])
        print("Email:", student["email"])

    print("\nStudent search completed!")


if __name__ == "__main__":

    print("\n===== UPDATE STUDENT TEST =====")

    # Get an existing student
    students = get_all_students()

    if students:

        test_student_id = students[0]["student_id"]

        result = update_student(
            student_id=test_student_id,
            student_name="Rahul Sharma Updated",
            roll_number="STU001",
            email="rahul.updated@example.com"
        )

        print("Success:", result["success"])
        print("Student ID:", result["student_id"])
        print("Student Name:", result["student_name"])
        print("Roll Number:", result["roll_number"])
        print("Email:", result["email"])
        print("Message:", result["message"])

    else:
        print("No students available to update.")

    print("\nStudent update test completed!")


if __name__ == "__main__":

    print("\n===== DELETE STUDENT TEST =====")

    students = get_all_students()

    if students:

        test_student_id = students[0]["student_id"]

        result = delete_student(test_student_id)

        print("Success:", result["success"])
        print("Student ID:", result["student_id"])
        print("Student Name:", result["student_name"])
        print("Roll Number:", result["roll_number"])
        print("Message:", result["message"])

        # Verify deletion
        remaining_students = get_all_students()

        deleted_student_exists = any(
            student["student_id"] == test_student_id
            for student in remaining_students
        )

        print("\nRemaining Students:", len(remaining_students))
        print("Deleted Student Still Exists:", deleted_student_exists)

    else:
        print("No students available to delete.")

    print("\nStudent deletion test completed!")
