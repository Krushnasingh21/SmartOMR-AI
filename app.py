
import streamlit as st

from config import (
    APP_TITLE,
    PROJECT_NAME,
    PROJECT_VERSION,
    create_required_directories
)


# ==========================================
# 1. INITIAL CONFIGURATION
# ==========================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📝",
    layout="wide"
)

# Create required folders
create_required_directories()


# ==========================================
# 2. SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("📝 SmartOMR AI")

st.sidebar.caption("Intelligent OMR Scanning & Evaluation")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Exam Management",
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

    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Exams", "0")
    col2.metric("Students", "0")
    col3.metric("Sheets Scanned", "0")
    col4.metric("Results Generated", "0")

    st.subheader("Getting Started")

    st.info(
        "Your SmartOMR AI platform is initialized. "
        "Exam management, image processing, and automatic "
        "evaluation will be developed in upcoming steps."
    )

    st.subheader("Development Status")

    st.write("Project setup completed.")

    st.progress(20)


# ==========================================
# 4. EXAM MANAGEMENT
# ==========================================

elif menu == "Exam Management":

    st.title("Exam Management")

    st.write("Create and manage examinations.")

    exam_name = st.text_input("Exam Name")

    total_questions = st.number_input(
        "Number of Questions",
        min_value=1,
        max_value=300,
        value=100
    )

    total_marks = st.number_input(
        "Total Marks",
        min_value=1,
        value=100
    )

    if st.button("Create Exam"):

        if exam_name.strip():

            st.success(
                f"Exam '{exam_name}' entered successfully!"
            )

            st.write("Questions:", total_questions)
            st.write("Total Marks:", total_marks)

            st.caption(
                "Database saving will be implemented in a later step."
            )

        else:
            st.warning("Please enter an exam name.")


# ==========================================
# 5. SCAN OMR
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
# 6. RESULTS
# ==========================================

elif menu == "Results":

    st.title("Examination Results")

    st.info(
        "Student results and automatic answer evaluation "
        "will be implemented in a later development phase."
    )


# ==========================================
# 7. ABOUT PROJECT
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
    st.write("- SQLite")

    st.write("Version:", PROJECT_VERSION)
    st.write("Project:", PROJECT_NAME)


# ==========================================
# 8. FOOTER
# ==========================================

st.sidebar.divider()

st.sidebar.caption(
    f"{PROJECT_NAME} | Version {PROJECT_VERSION}"
)
