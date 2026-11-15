
import streamlit as st
import pandas as pd

from config import (
    APP_TITLE,
    PROJECT_NAME,
    PROJECT_VERSION,
    create_required_directories
)

# Exam management functions
from database.exam_manager import (
    create_exam,
    get_all_exams,
    update_exam,
    delete_exam
)

# Student management functions
from database.student_manager import (
    create_student,
    get_all_students,
    search_students,
    update_student,
    delete_student
)

# Answer key management functions
from database.answer_key_manager import (
    create_answer_key,
    get_answer_key,
    get_all_answer_keys,
    update_answer_key,
    delete_answer_key
)


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
# 2. SIDEBAR NAVIGATION
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
# 3. DASHBOARD
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
        st.error(f"Unable to load dashboard data: {error}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Exams", total_exams)
    col2.metric("Students", total_students)
    col3.metric("Sheets Scanned", "0")
    col4.metric("Results Generated", "0")

    st.subheader("Getting Started")

    st.info(
        "Manage examinations, students and answer keys, scan OMR sheets, "
        "and evaluate student responses using SmartOMR AI."
    )

    st.subheader("Development Status")

    st.write(
        "Database-connected Exam Management, Student Management "
        "and Answer Key Management are available."
    )

    st.progress(45)


# ==========================================
# 4. EXAM MANAGEMENT
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
        st.error(f"Unable to retrieve exams: {error}")
        all_exams = []

    create_tab, view_tab, edit_tab, delete_tab = st.tabs(
        [
            "➕ Create Exam",
            "📋 View Exams",
            "✏️ Edit Exam",
            "🗑️ Delete Exam"
        ]
    )

    # ======================================
    # 4.1 CREATE EXAM
    # ======================================

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

                    st.warning("Please enter an exam name.")

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
                        st.error(f"Unable to create exam: {error}")

    # ======================================
    # 4.2 VIEW EXAMS
    # ======================================

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

            st.info(f"Total saved examinations: {len(all_exams)}")

        else:
            st.info("No examinations found. Create your first exam.")

    # ======================================
    # 4.3 EDIT EXAM
    # ======================================

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
                        st.warning("Exam name cannot be empty.")

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
                            st.error(f"Unable to update exam: {error}")

        else:
            st.info("No examinations available to update.")

    # ======================================
    # 4.4 DELETE EXAM
    # ======================================

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
                    result = delete_exam(selected_delete_id)
                    st.success(result["message"])
                    st.rerun()

                except Exception as error:
                    st.error(f"Unable to delete exam: {error}")

        else:
            st.info("No examinations available to delete.")


# ==========================================
# 5. STUDENT MANAGEMENT
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
        st.error(f"Unable to retrieve students: {error}")
        all_students = []

    # --------------------------------------
    # STUDENT MANAGEMENT TABS
    # --------------------------------------

    register_tab, view_tab, search_tab, edit_tab, delete_tab = st.tabs(
        [
            "➕ Register Student",
            "📋 View Students",
            "🔍 Search Students",
            "✏️ Edit Student",
            "🗑️ Delete Student"
        ]
    )

    # ======================================
    # 5.1 REGISTER STUDENT
    # ======================================

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

                    st.warning("Please enter the student name.")

                elif not roll_number.strip():

                    st.warning("Please enter the roll number.")

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

    # ======================================
    # 5.2 VIEW ALL STUDENTS
    # ======================================

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
                "No students registered yet. "
                "Register your first student."
            )

    # ======================================
    # 5.3 SEARCH STUDENTS
    # ======================================

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

                    st.warning("No matching students found.")

            except Exception as error:

                st.error(f"Student search failed: {error}")

        else:

            st.info(
                "Enter a student name or roll number to search."
            )

    # ======================================
    # 5.4 EDIT STUDENT
    # ======================================

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

                        st.warning("Student name cannot be empty.")

                    elif not updated_roll_number.strip():

                        st.warning("Roll number cannot be empty.")

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

            st.info("No students available to update.")

    # ======================================
    # 5.5 DELETE STUDENT
    # ======================================

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

            st.info("No students available to delete.")


# ==========================================
# 6. ANSWER KEY MANAGEMENT
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
        st.error(f"Unable to load answer key data: {error}")
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

    # ======================================
    # 6.1 CREATE ANSWER KEY
    # ======================================

    with create_tab:

        st.subheader("Create New Answer Key")

        if not all_exams:

            st.info("Please create an examination first.")

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

                st.write("Select the correct answer for each question.")

                with st.form("create_answer_key_form"):

                    answers = {}
                    question_columns = st.columns(4)

                    for question_number in range(
                        1, total_questions + 1
                    ):

                        column_index = (question_number - 1) % 4

                        with question_columns[column_index]:

                            selected_answer = st.selectbox(
                                f"Question {question_number}",
                                options=["-- Select --"] + options,
                                key=f"create_answer_{selected_exam_id}_q_{question_number}"
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

    # ======================================
    # 6.2 VIEW ANSWER KEYS
    # ======================================

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

                st.warning("The selected answer key could not be found.")

        else:

            st.info("No answer keys have been created yet.")

    # ======================================
    # 6.3 EDIT ANSWER KEY
    # ======================================

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
                        1, selected_exam["total_questions"] + 1
                    ):

                        column_index = (question_number - 1) % 4
                        current_answer = current_key["answers"].get(
                            question_number
                        )

                        with question_columns[column_index]:

                            # If exam settings changed and an old answer
                            # is no longer valid, require a valid selection.
                            select_options = options

                            if current_answer not in options:
                                select_options = ["-- Select --"] + options
                                selected_index = 0
                            else:
                                selected_index = options.index(current_answer)

                            updated_answers[question_number] = st.selectbox(
                                f"Question {question_number}",
                                options=select_options,
                                index=selected_index,
                                key=f"edit_answer_{selected_edit_id}_q_{question_number}"
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

            st.info("No answer keys available to edit.")

    # ======================================
    # 6.4 DELETE ANSWER KEY
    # ======================================

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

                    result = delete_answer_key(selected_delete_id)

                    st.success(result["message"])
                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Unable to delete answer key: {error}"
                    )

        else:

            st.info("No answer keys available to delete.")


# ==========================================
# 7. SCAN OMR
# ==========================================

elif menu == "Scan OMR":

    st.title("OMR Sheet Scanner")

    st.write(
        "Upload an OMR sheet or capture an image using your camera."
    )

    upload_tab, camera_tab = st.tabs(
        ["Upload Image", "Camera"]
    )

    with upload_tab:

        uploaded_file = st.file_uploader(
            "Upload OMR Sheet",
            type=["jpg", "jpeg", "png", "bmp"]
        )

        if uploaded_file is not None:

            st.image(
                uploaded_file,
                caption="Uploaded OMR Sheet",
                use_container_width=True
            )

            st.success("Image uploaded successfully!")

    with camera_tab:

        camera_image = st.camera_input(
            "Capture OMR Sheet"
        )

        if camera_image is not None:

            st.image(
                camera_image,
                caption="Captured OMR Sheet",
                use_container_width=True
            )


# ==========================================
# 8. RESULTS
# ==========================================

elif menu == "Results":

    st.title("Examination Results")

    st.info(
        "Student results and automatic answer evaluation "
        "will be implemented in a later development phase."
    )


# ==========================================
# 9. ABOUT PROJECT
# ==========================================

elif menu == "About Project":

    st.title("About SmartOMR AI")

    st.write(
        "SmartOMR AI is an AI-powered Optical Mark Recognition "
        "platform designed to scan OMR answer sheets, identify "
        "marked responses, evaluate answers, and generate reports."
    )

    st.subheader("Technology Stack")

    st.write("- Python")
    st.write("- Streamlit")
    st.write("- OpenCV")
    st.write("- NumPy and Pandas")
    st.write("- Scikit-learn")
    st.write("- SQLAlchemy")
    st.write("- SQLite")

    st.write("Version:", PROJECT_VERSION)
    st.write("Project:", PROJECT_NAME)


# ==========================================
# 10. FOOTER
# ==========================================

st.sidebar.divider()

st.sidebar.caption(
    f"{PROJECT_NAME} | Version {PROJECT_VERSION}"
)