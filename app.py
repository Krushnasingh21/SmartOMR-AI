
import streamlit as st
import pandas as pd
import cv2
import numpy as np
import tempfile
import os

from pathlib import Path

from config import (
    APP_TITLE,
    PROJECT_NAME,
    PROJECT_VERSION,
    create_required_directories
)

# ==========================================
# DATABASE IMPORTS
# ==========================================

from database.exam_manager import (
    create_exam,
    get_all_exams,
    update_exam,
    delete_exam
)

from database.student_manager import (
    create_student,
    get_all_students,
    search_students,
    update_student,
    delete_student
)

from database.answer_key_manager import (
    create_answer_key,
    get_answer_key,
    get_all_answer_keys,
    update_answer_key,
    delete_answer_key
)

# ==========================================
# OMR PIPELINE IMPORT
# ==========================================

from src.omr_pipeline import process_omr


# ==========================================
# 1. INITIAL CONFIGURATION
# ==========================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📝",
    layout="wide"
)

create_required_directories()


# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def get_answer_dataframe(detected_answers):

    rows = []

    for question, answer in sorted(detected_answers.items()):

        if answer == "UNANSWERED":
            status = "Unanswered"

        elif answer == "REVIEW_REQUIRED":
            status = "Review Required"

        elif answer == "MULTIPLE_MARKS":
            status = "Multiple Marks"

        else:
            status = "Answered"

        rows.append({
            "Question": question,
            "Detected Answer": answer,
            "Status": status
        })

    return pd.DataFrame(rows)


def display_omr_result(result, exam_name=None, student_name=None):

    if not result:
        st.info("No OMR result available.")
        return

    evaluation = result.get("evaluation")

    detected_answers = result.get("detected_answers", {})

    structure = result.get("structure", {})

    st.divider()

    st.subheader("OMR Processing Summary")

    if exam_name:
        st.write(f"**Examination:** {exam_name}")

    if student_name:
        st.write(f"**Student:** {student_name}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Questions",
        len(detected_answers)
    )

    answered_count = sum(
        1 for answer in detected_answers.values()
        if answer not in (
            "UNANSWERED",
            "REVIEW_REQUIRED",
            "MULTIPLE_MARKS"
        )
    )

    unanswered_count = sum(
        1 for answer in detected_answers.values()
        if answer == "UNANSWERED"
    )

    review_count = sum(
        1 for answer in detected_answers.values()
        if answer in (
            "REVIEW_REQUIRED",
            "MULTIPLE_MARKS"
        )
    )

    col2.metric("Answered", answered_count)
    col3.metric("Unanswered", unanswered_count)
    col4.metric("Review Required", review_count)

    # --------------------------------------
    # EVALUATION RESULT
    # --------------------------------------

    if evaluation:

        st.subheader("Examination Result")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Final Score",
            f"{evaluation['score']} / {evaluation['maximum_marks']}"
        )

        col2.metric(
            "Percentage",
            f"{evaluation['percentage']}%"
        )

        col3.metric(
            "Correct",
            evaluation["correct"]
        )

        col4.metric(
            "Incorrect",
            evaluation["incorrect"]
        )

        result_data = {
            "Category": [
                "Correct",
                "Incorrect",
                "Unanswered",
                "Review Required"
            ],
            "Count": [
                evaluation["correct"],
                evaluation["incorrect"],
                evaluation["unanswered"],
                evaluation["review_required"]
            ]
        }

        st.bar_chart(
            pd.DataFrame(result_data).set_index("Category")
        )

    # --------------------------------------
    # LAYOUT INFORMATION
    # --------------------------------------

    with st.expander("OMR Layout and Structure Details"):

        layout = result.get("layout", {})

        st.write(
            "**Detected Layout:**",
            layout.get("layout_name", "Unknown")
        )

        st.write(
            "**Layout Confidence:**",
            layout.get("confidence", 0)
        )

        st.write(
            "**Expected Bubble Positions:**",
            structure.get("expected_bubble_positions", 0)
        )

        st.write(
            "**Detected Bubble Positions:**",
            structure.get("detected_bubble_positions", 0)
        )

        st.write(
            "**Complete Question Groups:**",
            structure.get("detected_question_groups", 0)
        )

    # --------------------------------------
    # ALIGNED IMAGE
    # --------------------------------------

    aligned_image = result.get("aligned_image")

    if aligned_image is not None:

        st.subheader("Aligned OMR Sheet")

        display_image = cv2.cvtColor(
            aligned_image,
            cv2.COLOR_BGR2RGB
        )

        st.image(
            display_image,
            caption="Processed and aligned OMR sheet",
            use_container_width=True
        )

    # --------------------------------------
    # DETECTED ANSWERS
    # --------------------------------------

    st.subheader("Detected Answers")

    answer_df = get_answer_dataframe(
        detected_answers
    )

    st.dataframe(
        answer_df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------
    # CSV DOWNLOAD
    # --------------------------------------

    csv_data = answer_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Detected Answers CSV",
        data=csv_data,
        file_name="smartomr_detected_answers.csv",
        mime="text/csv",
        use_container_width=True
    )


# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("📝 SmartOMR AI")

st.sidebar.caption(
    "Intelligent OMR Scanning & Evaluation"
)

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Exam Management",
        "Student Management",
        "Answer Key Management",
        "Scan OMR",
        "Results",
        "About Project"
    ]
)


# ==========================================
# 4. DASHBOARD
# ==========================================

if menu == "Dashboard":

    st.title("SmartOMR AI Dashboard")

    st.write(
        "Welcome to SmartOMR AI – "
        "Your intelligent OMR scanning and evaluation platform."
    )

    st.divider()

    try:

        total_exams = len(get_all_exams())

        total_students = len(get_all_students())

    except Exception as error:

        total_exams = 0
        total_students = 0

        st.error(
            f"Unable to load dashboard data: {error}"
        )

    scanned_count = int(
        "last_omr_result" in st.session_state
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Exams",
        total_exams
    )

    col2.metric(
        "Students",
        total_students
    )

    col3.metric(
        "Sheets Processed This Session",
        scanned_count
    )

    col4.metric(
        "Results Generated This Session",
        scanned_count
    )

    st.subheader("Getting Started")

    st.info(
        "Manage examinations, students and answer keys, "
        "scan OMR sheets, and evaluate student responses "
        "using SmartOMR AI."
    )

    st.subheader("Available Modules")

    st.write("✅ Exam Management")

    st.write("✅ Student Management")

    st.write("✅ Answer Key Management")

    st.write("✅ OMR Image Processing Pipeline")

    st.write("✅ Automatic Answer Extraction")

    st.write("✅ Answer Evaluation")

    st.write("🔄 PDF and Excel report generation - upcoming")

    st.progress(65)


# ==========================================
# 5. EXAM MANAGEMENT
# ==========================================

elif menu == "Exam Management":

    st.title("📚 Exam Management")

    st.write(
        "Create, view, update and delete examinations."
    )

    st.divider()

    try:
        all_exams = get_all_exams()

    except Exception as error:

        st.error(
            f"Unable to retrieve exams: {error}"
        )

        all_exams = []

    create_tab, view_tab, edit_tab, delete_tab = st.tabs(
        [
            "➕ Create Exam",
            "📋 View Exams",
            "✏️ Edit Exam",
            "🗑️ Delete Exam"
        ]
    )

    # --------------------------------------
    # CREATE EXAM
    # --------------------------------------

    with create_tab:

        st.subheader("Create New Examination")

        with st.form("create_exam_form"):

            exam_name = st.text_input(
                "Exam Name",
                placeholder="Enter examination name"
            )

            total_questions = st.number_input(
                "Number of Questions",
                min_value=1,
                max_value=300,
                value=100,
                step=1
            )

            options_per_question = st.selectbox(
                "Options Per Question",
                [2, 3, 4, 5]
            )

            marks_per_correct = st.number_input(
                "Marks Per Correct Answer",
                min_value=0.1,
                value=1.0,
                step=0.5
            )

            negative_marking = st.number_input(
                "Negative Marking",
                min_value=0.0,
                value=0.0,
                step=0.25
            )

            submitted = st.form_submit_button(
                "Create Examination",
                use_container_width=True
            )

            if submitted:

                if not exam_name.strip():

                    st.warning(
                        "Please enter an exam name."
                    )

                else:

                    try:

                        result = create_exam(
                            exam_name=exam_name,
                            total_questions=int(total_questions),
                            options_per_question=options_per_question,
                            marks_per_correct=marks_per_correct,
                            negative_marking=negative_marking
                        )

                        st.success(
                            f"Exam created successfully! "
                            f"Exam ID: {result['exam_id']}"
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Unable to create exam: {error}"
                        )

    # --------------------------------------
    # VIEW EXAMS
    # --------------------------------------

    with view_tab:

        st.subheader("Saved Examinations")

        if all_exams:

            exam_df = pd.DataFrame(all_exams)

            exam_df = exam_df.rename(
                columns={
                    "exam_id": "Exam ID",
                    "exam_name": "Exam Name",
                    "total_questions": "Questions",
                    "options_per_question": "Options",
                    "marks_per_correct": "Marks / Correct",
                    "negative_marking": "Negative Marking",
                    "created_at": "Created At"
                }
            )

            st.dataframe(
                exam_df,
                use_container_width=True,
                hide_index=True
            )

            st.info(
                f"Total saved examinations: {len(all_exams)}"
            )

        else:

            st.info(
                "No examinations found. Create your first exam."
            )

    # --------------------------------------
    # EDIT EXAM
    # --------------------------------------

    with edit_tab:

        st.subheader("Update Examination")

        if all_exams:

            exam_lookup = {
                exam["exam_id"]: exam
                for exam in all_exams
            }

            selected_exam_id = st.selectbox(
                "Select Examination",
                options=list(exam_lookup.keys()),
                format_func=lambda exam_id: (
                    f"{exam_lookup[exam_id]['exam_name']} "
                    f"(ID: {exam_id})"
                ),
                key="edit_exam_selection"
            )

            selected_exam = exam_lookup[selected_exam_id]

            with st.form("update_exam_form"):

                updated_name = st.text_input(
                    "Exam Name",
                    value=selected_exam["exam_name"]
                )

                updated_questions = st.number_input(
                    "Number of Questions",
                    min_value=1,
                    max_value=300,
                    value=selected_exam["total_questions"],
                    step=1
                )

                option_choices = [2, 3, 4, 5]

                current_options = selected_exam["options_per_question"]

                updated_options = st.selectbox(
                    "Options Per Question",
                    option_choices,
                    index=(
                        option_choices.index(current_options)
                        if current_options in option_choices
                        else 2
                    )
                )

                updated_marks = st.number_input(
                    "Marks Per Correct Answer",
                    min_value=0.1,
                    value=float(selected_exam["marks_per_correct"]),
                    step=0.5
                )

                updated_negative = st.number_input(
                    "Negative Marking",
                    min_value=0.0,
                    value=float(selected_exam["negative_marking"]),
                    step=0.25
                )

                update_submitted = st.form_submit_button(
                    "Update Examination",
                    use_container_width=True
                )

                if update_submitted:

                    if not updated_name.strip():

                        st.warning(
                            "Exam name cannot be empty."
                        )

                    else:

                        try:

                            result = update_exam(
                                exam_id=selected_exam_id,
                                exam_name=updated_name,
                                total_questions=int(updated_questions),
                                options_per_question=updated_options,
                                marks_per_correct=updated_marks,
                                negative_marking=updated_negative
                            )

                            st.success(result["message"])

                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"Unable to update exam: {error}"
                            )

        else:

            st.info(
                "No examinations available to update."
            )

    # --------------------------------------
    # DELETE EXAM
    # --------------------------------------

    with delete_tab:

        st.subheader("Delete Examination")

        if all_exams:

            exam_lookup = {
                exam["exam_id"]: exam
                for exam in all_exams
            }

            selected_delete_id = st.selectbox(
                "Select Examination to Delete",
                options=list(exam_lookup.keys()),
                format_func=lambda exam_id: (
                    f"{exam_lookup[exam_id]['exam_name']} "
                    f"(ID: {exam_id})"
                ),
                key="delete_exam_selection"
            )

            selected_delete_exam = exam_lookup[selected_delete_id]

            st.warning(
                f"You are about to delete: "
                f"{selected_delete_exam['exam_name']}"
            )

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this examination.",
                key="confirm_delete_exam"
            )

            if st.button(
                "Delete Examination",
                type="primary",
                disabled=not confirm_delete
            ):

                try:

                    result = delete_exam(
                        selected_delete_id
                    )

                    st.success(result["message"])

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Unable to delete exam: {error}"
                    )

        else:

            st.info(
                "No examinations available to delete."
            )


# ==========================================
# 6. STUDENT MANAGEMENT
# ==========================================

elif menu == "Student Management":

    st.title("👨‍🎓 Student Management")

    st.write(
        "Register, view, search, update and delete student records."
    )

    st.divider()

    try:

        all_students = get_all_students()

    except Exception as error:

        st.error(
            f"Unable to retrieve students: {error}"
        )

        all_students = []

    register_tab, view_tab, search_tab, edit_tab, delete_tab = st.tabs(
        [
            "➕ Register Student",
            "📋 View Students",
            "🔍 Search Students",
            "✏️ Edit Student",
            "🗑️ Delete Student"
        ]
    )

    # --------------------------------------
    # REGISTER STUDENT
    # --------------------------------------

    with register_tab:

        st.subheader("Register New Student")

        with st.form("register_student_form"):

            student_name = st.text_input(
                "Student Name",
                placeholder="Enter full name"
            )

            roll_number = st.text_input(
                "Roll Number",
                placeholder="Enter unique roll number"
            )

            email = st.text_input(
                "Email Address",
                placeholder="Enter email address (optional)"
            )

            register_submitted = st.form_submit_button(
                "Register Student",
                use_container_width=True
            )

            if register_submitted:

                if not student_name.strip():

                    st.warning(
                        "Please enter the student name."
                    )

                elif not roll_number.strip():

                    st.warning(
                        "Please enter the roll number."
                    )

                else:

                    try:

                        result = create_student(
                            student_name=student_name,
                            roll_number=roll_number,
                            email=email
                        )

                        st.success(
                            f"{result['message']} "
                            f"Student ID: {result['student_id']}"
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Unable to register student: {error}"
                        )

    # --------------------------------------
    # VIEW STUDENTS
    # --------------------------------------

    with view_tab:

        st.subheader("Registered Students")

        if all_students:

            student_df = pd.DataFrame(all_students)

            student_df = student_df.rename(
                columns={
                    "student_id": "Student ID",
                    "student_name": "Student Name",
                    "roll_number": "Roll Number",
                    "email": "Email"
                }
            )

            st.dataframe(
                student_df,
                use_container_width=True,
                hide_index=True
            )

            st.info(
                f"Total registered students: {len(all_students)}"
            )

        else:

            st.info(
                "No students registered yet. Register your first student."
            )

    # --------------------------------------
    # SEARCH STUDENTS
    # --------------------------------------

    with search_tab:

        st.subheader("Search Registered Students")

        search_query = st.text_input(
            "Search by Student Name or Roll Number",
            placeholder="Enter name or roll number"
        )

        if search_query.strip():

            try:

                search_results = search_students(search_query)

                if search_results:

                    st.success(
                        f"Found {len(search_results)} student(s)."
                    )

                    search_df = pd.DataFrame(search_results)

                    search_df = search_df.rename(
                        columns={
                            "student_id": "Student ID",
                            "student_name": "Student Name",
                            "roll_number": "Roll Number",
                            "email": "Email"
                        }
                    )

                    st.dataframe(
                        search_df,
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.warning(
                        "No matching students found."
                    )

            except Exception as error:

                st.error(
                    f"Student search failed: {error}"
                )

        else:

            st.info(
                "Enter a student name or roll number to search."
            )

    # --------------------------------------
    # EDIT STUDENT
    # --------------------------------------

    with edit_tab:

        st.subheader("Update Student Information")

        if all_students:

            student_lookup = {
                student["student_id"]: student
                for student in all_students
            }

            selected_student_id = st.selectbox(
                "Select Student",
                options=list(student_lookup.keys()),
                format_func=lambda student_id: (
                    f"{student_lookup[student_id]['student_name']} "
                    f"({student_lookup[student_id]['roll_number']})"
                ),
                key="edit_student_selection"
            )

            selected_student = student_lookup[selected_student_id]

            with st.form("update_student_form"):

                updated_student_name = st.text_input(
                    "Student Name",
                    value=selected_student["student_name"]
                )

                updated_roll_number = st.text_input(
                    "Roll Number",
                    value=selected_student["roll_number"]
                )

                updated_email = st.text_input(
                    "Email Address",
                    value=selected_student["email"] or ""
                )

                update_student_submitted = st.form_submit_button(
                    "Update Student",
                    use_container_width=True
                )

                if update_student_submitted:

                    if not updated_student_name.strip():

                        st.warning(
                            "Student name cannot be empty."
                        )

                    elif not updated_roll_number.strip():

                        st.warning(
                            "Roll number cannot be empty."
                        )

                    else:

                        try:

                            result = update_student(
                                student_id=selected_student_id,
                                student_name=updated_student_name,
                                roll_number=updated_roll_number,
                                email=updated_email
                            )

                            st.success(result["message"])

                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"Unable to update student: {error}"
                            )

        else:

            st.info(
                "No students available to update."
            )

    # --------------------------------------
    # DELETE STUDENT
    # --------------------------------------

    with delete_tab:

        st.subheader("Delete Student")

        if all_students:

            student_lookup = {
                student["student_id"]: student
                for student in all_students
            }

            selected_delete_student_id = st.selectbox(
                "Select Student to Delete",
                options=list(student_lookup.keys()),
                format_func=lambda student_id: (
                    f"{student_lookup[student_id]['student_name']} "
                    f"({student_lookup[student_id]['roll_number']})"
                ),
                key="delete_student_selection"
            )

            selected_delete_student = student_lookup[
                selected_delete_student_id
            ]

            st.warning(
                f"You are about to delete student: "
                f"{selected_delete_student['student_name']}"
            )

            confirm_student_delete = st.checkbox(
                "I confirm that I want to delete this student.",
                key="confirm_delete_student"
            )

            if st.button(
                "Delete Student",
                type="primary",
                disabled=not confirm_student_delete
            ):

                try:

                    result = delete_student(
                        selected_delete_student_id
                    )

                    st.success(result["message"])

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Unable to delete student: {error}"
                    )

        else:

            st.info(
                "No students available to delete."
            )


# ==========================================
# 7. ANSWER KEY MANAGEMENT
# ==========================================

elif menu == "Answer Key Management":

    st.title("🔑 Answer Key Management")

    st.write(
        "Create, view, update and delete examination answer keys."
    )

    st.divider()

    try:

        all_exams = get_all_exams()

        all_answer_keys = get_all_answer_keys()

    except Exception as error:

        st.error(
            f"Unable to load answer key data: {error}"
        )

        all_exams = []
        all_answer_keys = []

    create_tab, view_tab, edit_tab, delete_tab = st.tabs(
        [
            "➕ Create Answer Key",
            "📋 View Answer Keys",
            "✏️ Edit Answer Key",
            "🗑️ Delete Answer Key"
        ]
    )

    # --------------------------------------
    # CREATE ANSWER KEY
    # --------------------------------------

    with create_tab:

        st.subheader("Create New Answer Key")

        if not all_exams:

            st.info(
                "Please create an examination first."
            )

        else:

            exam_lookup = {
                exam["exam_id"]: exam
                for exam in all_exams
            }

            selected_exam_id = st.selectbox(
                "Select Examination",
                options=list(exam_lookup.keys()),
                format_func=lambda exam_id: (
                    f"{exam_lookup[exam_id]['exam_name']} "
                    f"(ID: {exam_id})"
                ),
                key="create_answer_exam"
            )

            selected_exam = exam_lookup[selected_exam_id]

            existing_key = get_answer_key(selected_exam_id)

            if existing_key:

                st.warning(
                    "An answer key already exists for this examination. "
                    "Use the Edit Answer Key tab to modify it."
                )

            else:

                total_questions = selected_exam["total_questions"]

                total_options = selected_exam["options_per_question"]

                options = ["A", "B", "C", "D", "E"][:total_options]

                st.info(
                    f"Questions: {total_questions} | "
                    f"Available options: {', '.join(options)}"
                )

                st.write(
                    "Select the correct answer for each question."
                )

                with st.form("create_answer_key_form"):

                    answers = {}

                    question_columns = st.columns(4)

                    for question_number in range(
                        1,
                        total_questions + 1
                    ):

                        column_index = (question_number - 1) % 4

                        with question_columns[column_index]:

                            selected_answer = st.selectbox(
                                f"Question {question_number}",
                                options=["-- Select --"] + options,
                                key=(
                                    f"create_answer_{selected_exam_id}"
                                    f"_q_{question_number}"
                                )
                            )

                            answers[question_number] = selected_answer

                    submitted = st.form_submit_button(
                        "Save Answer Key",
                        use_container_width=True
                    )

                    if submitted:

                        unanswered = [
                            question
                            for question, answer in answers.items()
                            if answer == "-- Select --"
                        ]

                        if unanswered:

                            st.error(
                                "Please select answers for all questions. "
                                f"Missing questions: {unanswered}"
                            )

                        else:

                            try:

                                result = create_answer_key(
                                    exam_id=selected_exam_id,
                                    answers=answers
                                )

                                st.success(result["message"])

                                st.rerun()

                            except Exception as error:

                                st.error(
                                    f"Unable to save answer key: {error}"
                                )

    # --------------------------------------
    # VIEW ANSWER KEYS
    # --------------------------------------

    with view_tab:

        st.subheader("Saved Answer Keys")

        if all_answer_keys:

            display_data = [
                {
                    "Answer Key ID": key["answer_key_id"],
                    "Exam ID": key["exam_id"],
                    "Exam Name": key["exam_name"],
                    "Total Questions": key["total_questions"]
                }
                for key in all_answer_keys
            ]

            st.dataframe(
                pd.DataFrame(display_data),
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("View Individual Answer Key")

            view_exam_lookup = {
                key["exam_id"]: key["exam_name"]
                for key in all_answer_keys
            }

            selected_view_id = st.selectbox(
                "Select Examination",
                options=list(view_exam_lookup.keys()),
                format_func=lambda exam_id: (
                    f"{view_exam_lookup[exam_id]} (ID: {exam_id})"
                ),
                key="view_answer_key_exam"
            )

            selected_key = get_answer_key(selected_view_id)

            if selected_key:

                answer_data = [
                    {
                        "Question": question,
                        "Correct Answer": answer
                    }
                    for question, answer in sorted(
                        selected_key["answers"].items()
                    )
                ]

                st.dataframe(
                    pd.DataFrame(answer_data),
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.warning(
                    "The selected answer key could not be found."
                )

        else:

            st.info(
                "No answer keys have been created yet."
            )

    # --------------------------------------
    # EDIT ANSWER KEY
    # --------------------------------------

    with edit_tab:

        st.subheader("Edit Existing Answer Key")

        if all_answer_keys:

            edit_exam_lookup = {
                key["exam_id"]: key["exam_name"]
                for key in all_answer_keys
            }

            selected_edit_id = st.selectbox(
                "Select Examination",
                options=list(edit_exam_lookup.keys()),
                format_func=lambda exam_id: (
                    f"{edit_exam_lookup[exam_id]} (ID: {exam_id})"
                ),
                key="edit_answer_key_exam"
            )

            selected_exam = next(
                (
                    exam for exam in all_exams
                    if exam["exam_id"] == selected_edit_id
                ),
                None
            )

            current_key = get_answer_key(selected_edit_id)

            if selected_exam is None or current_key is None:

                st.error(
                    "The examination or its answer key could not be found."
                )

            else:

                options = [
                    "A", "B", "C", "D", "E"
                ][:selected_exam["options_per_question"]]

                st.info(
                    f"Total Questions: {selected_exam['total_questions']}"
                )

                with st.form("edit_answer_key_form"):

                    updated_answers = {}

                    question_columns = st.columns(4)

                    for question_number in range(
                        1,
                        selected_exam["total_questions"] + 1
                    ):

                        column_index = (question_number - 1) % 4

                        current_answer = current_key["answers"].get(
                            question_number
                        )

                        with question_columns[column_index]:

                            if current_answer not in options:

                                select_options = ["-- Select --"] + options

                                selected_index = 0

                            else:

                                select_options = options

                                selected_index = options.index(
                                    current_answer
                                )

                            updated_answers[question_number] = st.selectbox(
                                f"Question {question_number}",
                                options=select_options,
                                index=selected_index,
                                key=(
                                    f"edit_answer_{selected_edit_id}"
                                    f"_q_{question_number}"
                                )
                            )

                    update_submitted = st.form_submit_button(
                        "Update Answer Key",
                        use_container_width=True
                    )

                    if update_submitted:

                        unanswered = [
                            question
                            for question, answer in updated_answers.items()
                            if answer == "-- Select --"
                        ]

                        if unanswered:

                            st.error(
                                "Please select valid answers for all questions. "
                                f"Missing questions: {unanswered}"
                            )

                        else:

                            try:

                                result = update_answer_key(
                                    exam_id=selected_edit_id,
                                    updated_answers=updated_answers
                                )

                                st.success(result["message"])

                                st.rerun()

                            except Exception as error:

                                st.error(
                                    f"Unable to update answer key: {error}"
                                )

        else:

            st.info(
                "No answer keys available to edit."
            )

    # --------------------------------------
    # DELETE ANSWER KEY
    # --------------------------------------

    with delete_tab:

        st.subheader("Delete Answer Key")

        if all_answer_keys:

            delete_exam_lookup = {
                key["exam_id"]: key["exam_name"]
                for key in all_answer_keys
            }

            selected_delete_id = st.selectbox(
                "Select Examination",
                options=list(delete_exam_lookup.keys()),
                format_func=lambda exam_id: (
                    f"{delete_exam_lookup[exam_id]} (ID: {exam_id})"
                ),
                key="delete_answer_key_exam"
            )

            st.warning(
                "You are about to delete the answer key associated "
                "with this examination. The examination itself will not "
                "be deleted."
            )

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this answer key.",
                key="confirm_delete_answer_key"
            )

            if st.button(
                "Delete Answer Key",
                type="primary",
                disabled=not confirm_delete
            ):

                try:

                    result = delete_answer_key(
                        selected_delete_id
                    )

                    st.success(result["message"])

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Unable to delete answer key: {error}"
                    )

        else:

            st.info(
                "No answer keys available to delete."
            )


# ==========================================
# 8. SCAN OMR
# ==========================================

elif menu == "Scan OMR":

    st.title("📷 SmartOMR AI - OMR Scanner")

    st.write(
        "Upload an OMR sheet or capture it using your camera. "
        "SmartOMR AI will automatically detect and evaluate answers."
    )

    st.divider()

    # --------------------------------------
    # SELECT INPUT METHOD
    # --------------------------------------

    upload_tab, camera_tab = st.tabs(
        [
            "📁 Upload OMR Sheet",
            "📸 Camera Capture"
        ]
    )

    uploaded_file = None
    camera_image = None

    with upload_tab:

        uploaded_file = st.file_uploader(
            "Upload OMR Sheet",
            type=[
                "jpg",
                "jpeg",
                "png",
                "bmp",
                "pdf"
            ],
            help="Supported formats: JPG, JPEG, PNG, BMP and PDF"
        )

        if uploaded_file is not None:

            st.success(
                f"File selected: {uploaded_file.name}"
            )

            if uploaded_file.type == "application/pdf":

                st.info(
                    "PDF selected. The first page will be processed."
                )

            else:

                st.image(
                    uploaded_file,
                    caption="Uploaded OMR Sheet",
                    use_container_width=True
                )

    with camera_tab:

        camera_image = st.camera_input(
            "Capture OMR Sheet"
        )

        if camera_image is not None:

            st.success(
                "Camera image captured successfully."
            )

    # --------------------------------------
    # SELECT EXAMINATION
    # --------------------------------------

    st.divider()

    st.subheader("Examination Configuration")

    try:

        available_exams = get_all_exams()

        available_students = get_all_students()

    except Exception as error:

        st.error(
            f"Unable to load examination or student data: {error}"
        )

        available_exams = []
        available_students = []

    if not available_exams:

        st.warning(
            "No examinations found. Please create an examination first."
        )

    else:

        exam_lookup = {
            exam["exam_id"]: exam
            for exam in available_exams
        }

        selected_exam_id = st.selectbox(
            "Select Examination",
            options=list(exam_lookup.keys()),
            format_func=lambda exam_id: (
                f"{exam_lookup[exam_id]['exam_name']} "
                f"({exam_lookup[exam_id]['total_questions']} Questions)"
            ),
            key="scan_exam_selection"
        )

        selected_exam = exam_lookup[selected_exam_id]

        st.write(
            f"**Total Questions:** {selected_exam['total_questions']}"
        )

        st.write(
            f"**Options Per Question:** "
            f"{selected_exam['options_per_question']}"
        )

        st.write(
            f"**Marks Per Correct Answer:** "
            f"{selected_exam['marks_per_correct']}"
        )

        st.write(
            f"**Negative Marking:** "
            f"{selected_exam['negative_marking']}"
        )

        # ----------------------------------
        # SELECT STUDENT
        # ----------------------------------

        student_options = {
            student["student_id"]: student
            for student in available_students
        }

        selected_student_id = None

        if student_options:

            selected_student_id = st.selectbox(
                "Select Student (Optional)",
                options=[None] + list(student_options.keys()),
                format_func=lambda student_id: (
                    "Not selected"
                    if student_id is None
                    else (
                        f"{student_options[student_id]['student_name']} "
                        f"({student_options[student_id]['roll_number']})"
                    )
                ),
                key="scan_student_selection"
            )

        # ----------------------------------
        # CHECK INPUT
        # ----------------------------------

        selected_input = (
            uploaded_file
            if uploaded_file is not None
            else camera_image
        )

        if uploaded_file is not None and camera_image is not None:

            st.warning(
                "Both an uploaded file and a camera image are selected. "
                "The uploaded file will be processed."
            )

        # ----------------------------------
        # PROCESS OMR
        # ----------------------------------

        st.divider()

        if st.button(
            "🚀 Process OMR Sheet",
            type="primary",
            use_container_width=True,
            disabled=selected_input is None
        ):

            if selected_exam["total_questions"] != 100:

                st.error(
                    "The current OMR pipeline supports exactly 100 "
                    "questions. Please select a compatible examination."
                )

            elif selected_exam["options_per_question"] != 4:

                st.error(
                    "The current OMR template supports four options "
                    "(A, B, C, D) per question."
                )

            else:

                try:

                    # Retrieve saved answer key
                    selected_key = get_answer_key(
                        selected_exam_id
                    )

                    if not selected_key:

                        st.error(
                            "No answer key exists for this examination. "
                            "Please create an answer key first."
                        )

                    else:

                        answer_key = selected_key["answers"]

                        st.info(
                            "Starting OMR processing..."
                        )

                        progress_bar = st.progress(10)

                        # ----------------------------------
                        # PREPARE INPUT
                        # ----------------------------------

                        temporary_pdf_path = None

                        try:

                            file_name = getattr(
                                selected_input,
                                "name",
                                "camera_capture.png"
                            )

                            file_extension = Path(
                                file_name
                            ).suffix.lower()

                            file_bytes = selected_input.getvalue()

                            if file_extension == ".pdf":

                                # Save uploaded PDF temporarily
                                with tempfile.NamedTemporaryFile(
                                    suffix=".pdf",
                                    delete=False
                                ) as temporary_file:

                                    temporary_file.write(
                                        file_bytes
                                    )

                                    temporary_pdf_path = temporary_file.name

                                input_source = temporary_pdf_path

                            else:

                                # Decode uploaded/camera image
                                image_array = np.frombuffer(
                                    file_bytes,
                                    dtype=np.uint8
                                )

                                decoded_image = cv2.imdecode(
                                    image_array,
                                    cv2.IMREAD_COLOR
                                )

                                if decoded_image is None:

                                    raise ValueError(
                                        "Unable to decode the uploaded image."
                                    )

                                input_source = decoded_image

                            progress_bar.progress(30)

                            # ----------------------------------
                            # RUN COMPLETE OMR PIPELINE
                            # ----------------------------------

                            result = process_omr(
                                input_source=input_source,
                                answer_key=answer_key,
                                marks_per_correct=float(
                                    selected_exam["marks_per_correct"]
                                ),
                                marks_per_wrong=0,
                                negative_marking=float(
                                    selected_exam["negative_marking"]
                                )
                            )

                            progress_bar.progress(100)

                            # ----------------------------------
                            # SAVE RESULT IN SESSION
                            # ----------------------------------

                            student_name = None

                            if selected_student_id is not None:

                                student_name = student_options[
                                    selected_student_id
                                ]["student_name"]

                            st.session_state["last_omr_result"] = result

                            st.session_state["last_omr_exam_name"] = (
                                selected_exam["exam_name"]
                            )

                            st.session_state["last_omr_student_name"] = (
                                student_name
                            )

                            st.session_state["last_omr_file_name"] = (
                                file_name
                            )

                            st.success(
                                "OMR processing completed successfully!"
                            )

                        finally:

                            if temporary_pdf_path and os.path.exists(
                                temporary_pdf_path
                            ):

                                os.remove(
                                    temporary_pdf_path
                                )

                except Exception as error:

                    st.error(
                        f"OMR processing failed: {error}"
                    )

        # ----------------------------------
        # DISPLAY CURRENT SESSION RESULT
        # ----------------------------------

        if "last_omr_result" in st.session_state:

            st.divider()

            st.subheader("Latest Processing Result")

            st.caption(
                f"File: {st.session_state.get('last_omr_file_name', 'Unknown')}"
            )

            display_omr_result(
                result=st.session_state["last_omr_result"],
                exam_name=st.session_state.get(
                    "last_omr_exam_name"
                ),
                student_name=st.session_state.get(
                    "last_omr_student_name"
                )
            )


# ==========================================
# 9. RESULTS
# ==========================================

elif menu == "Results":

    st.title("📊 Examination Results")

    st.write(
        "View the latest OMR processing result generated "
        "during this application session."
    )

    st.divider()

    if "last_omr_result" in st.session_state:

        display_omr_result(
            result=st.session_state["last_omr_result"],
            exam_name=st.session_state.get(
                "last_omr_exam_name"
            ),
            student_name=st.session_state.get(
                "last_omr_student_name"
            )
        )

    else:

        st.info(
            "No results are available in this session. "
            "Go to Scan OMR and process an OMR sheet first."
        )


# ==========================================
# 10. ABOUT PROJECT
# ==========================================

elif menu == "About Project":

    st.title("About SmartOMR AI")

    st.write(
        "SmartOMR AI is an AI-powered Optical Mark Recognition "
        "platform designed to scan OMR answer sheets, identify "
        "marked responses, evaluate answers, and generate reports."
    )

    st.subheader("Core Features")

    st.write("- OMR Image and PDF Upload")

    st.write("- Camera-Based OMR Capture")

    st.write("- OMR Layout Detection")

    st.write("- Image Processing and Alignment")

    st.write("- Bubble Detection and Answer Extraction")

    st.write("- Automatic Answer Key Evaluation")

    st.write("- Uncertain and Multiple Mark Detection")

    st.write("- Examination and Student Management")

    st.subheader("Technology Stack")

    st.write("- Python")

    st.write("- Streamlit")

    st.write("- OpenCV")

    st.write("- NumPy and Pandas")

    st.write("- Scikit-learn")

    st.write("- SQLAlchemy")

    st.write("- SQLite")

    st.write("- PyMuPDF")

    st.write("- Plotly")

    st.write("Version:", PROJECT_VERSION)

    st.write("Project:", PROJECT_NAME)


# ==========================================
# 11. SIDEBAR FOOTER
# ==========================================

st.sidebar.divider()

st.sidebar.caption(
    f"{PROJECT_NAME} | Version {PROJECT_VERSION}"
)
