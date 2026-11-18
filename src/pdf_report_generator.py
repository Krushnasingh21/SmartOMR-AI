
from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)

from config import REPORT_DIR, create_required_directories


def generate_student_result_pdf(result, output_path=None):

    """
    Generate an individual student OMR examination result PDF.

    Parameters:
        result: Dictionary containing saved OMR result details.
        output_path: Optional custom PDF output path.

    Returns:
        Dictionary containing success status and PDF path.
    """

    try:

        create_required_directories()

        if not isinstance(result, dict):
            raise ValueError("Result must be a dictionary.")

        required_fields = [
            "result_id",
            "exam_name",
            "student_name",
            "roll_number",
            "detected_answers",
            "correct",
            "incorrect",
            "unanswered",
            "review_required",
            "score",
            "maximum_marks",
            "percentage"
        ]

        missing_fields = [
            field for field in required_fields
            if field not in result
        ]

        if missing_fields:
            raise ValueError(
                f"Missing result fields: {missing_fields}"
            )

        if output_path is None:

            output_path = (
                Path(REPORT_DIR)
                / f"student_result_{result['result_id']}.pdf"
            )

        else:

            output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # ----------------------------------
        # PDF DOCUMENT
        # ----------------------------------

        document = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=0.55 * inch,
            leftMargin=0.55 * inch,
            topMargin=0.55 * inch,
            bottomMargin=0.55 * inch
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=20,
            leading=25,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17365D"),
            spaceAfter=8
        )

        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#666666"),
            spaceAfter=15
        )

        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#17365D"),
            spaceBefore=12,
            spaceAfter=8
        )

        normal_style = styles["Normal"]

        story = []

        # ----------------------------------
        # REPORT HEADER
        # ----------------------------------

        story.append(
            Paragraph(
                "SMARTOMR AI",
                title_style
            )
        )

        story.append(
            Paragraph(
                "STUDENT EXAMINATION RESULT REPORT",
                subtitle_style
            )
        )

        story.append(
            HRFlowable(
                width="100%",
                thickness=1,
                color=colors.HexColor("#17365D")
            )
        )

        story.append(Spacer(1, 15))

        # ----------------------------------
        # STUDENT INFORMATION
        # ----------------------------------

        story.append(
            Paragraph(
                "1. Student and Examination Details",
                heading_style
            )
        )

        evaluated_at = result.get("evaluated_at")

        if evaluated_at:

            if isinstance(evaluated_at, datetime):
                evaluated_at = evaluated_at.strftime(
                    "%d-%m-%Y %I:%M %p"
                )

            else:
                try:
                    evaluated_at = datetime.fromisoformat(
                        str(evaluated_at)
                    ).strftime("%d-%m-%Y %I:%M %p")

                except ValueError:
                    evaluated_at = str(evaluated_at)

        else:
            evaluated_at = "Not available"

        student_data = [
            ["Student Name", str(result["student_name"])],
            ["Roll Number", str(result["roll_number"])],
            ["Examination", str(result["exam_name"])],
            ["Result ID", str(result["result_id"])],
            ["Evaluation Date", evaluated_at]
        ]

        student_table = Table(
            student_data,
            colWidths=[2 * inch, 4.8 * inch]
        )

        student_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (0, -1),
                 colors.HexColor("#EAF0F7")),

                ("TEXTCOLOR", (0, 0), (0, -1),
                 colors.HexColor("#17365D")),

                ("FONTNAME", (0, 0), (0, -1),
                 "Helvetica-Bold"),

                ("FONTNAME", (1, 0), (1, -1),
                 "Helvetica"),

                ("FONTSIZE", (0, 0), (-1, -1), 9),

                ("GRID", (0, 0), (-1, -1), 0.5,
                 colors.HexColor("#CCCCCC")),

                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                ("TOPPADDING", (0, 0), (-1, -1), 8),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),

                ("LEFTPADDING", (0, 0), (-1, -1), 8)
            ])
        )

        story.append(student_table)

        # ----------------------------------
        # PERFORMANCE SUMMARY
        # ----------------------------------

        story.append(
            Paragraph(
                "2. Performance Summary",
                heading_style
            )
        )

        performance_data = [
            ["Metric", "Result"],
            ["Total Questions",
             len(result["detected_answers"])],

            ["Correct Answers", result["correct"]],

            ["Incorrect Answers", result["incorrect"]],

            ["Unanswered Questions", result["unanswered"]],

            ["Review Required", result["review_required"]],

            ["Final Score",
             f"{result['score']} / {result['maximum_marks']}"],

            ["Percentage",
             f"{float(result['percentage']):.2f}%"]
        ]

        performance_table = Table(
            performance_data,
            colWidths=[3.4 * inch, 3.4 * inch]
        )

        performance_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0),
                 colors.HexColor("#17365D")),

                ("TEXTCOLOR", (0, 0), (-1, 0),
                 colors.white),

                ("FONTNAME", (0, 0), (-1, 0),
                 "Helvetica-Bold"),

                ("FONTNAME", (0, 1), (-1, -1),
                 "Helvetica"),

                ("FONTSIZE", (0, 0), (-1, -1), 9),

                ("GRID", (0, 0), (-1, -1), 0.5,
                 colors.HexColor("#CCCCCC")),

                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [
                     colors.white,
                     colors.HexColor("#F3F6FA")
                 ]),

                ("ALIGN", (1, 0), (1, -1), "CENTER"),

                ("TOPPADDING", (0, 0), (-1, -1), 8),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 8)
            ])
        )

        story.append(performance_table)

        # ----------------------------------
        # QUESTION-WISE ANSWERS
        # ----------------------------------

        story.append(
            Paragraph(
                "3. Question-wise Detected Answers",
                heading_style
            )
        )

        detected_answers = result["detected_answers"]

        answer_data = [
            ["Question", "Detected Answer", "Status"]
        ]

        for question, answer in sorted(
            detected_answers.items(),
            key=lambda item: int(item[0])
        ):

            if answer == "UNANSWERED":
                status = "Unanswered"

            elif answer == "REVIEW_REQUIRED":
                status = "Review Required"

            elif answer == "MULTIPLE_MARKS":
                status = "Multiple Marks"

            else:
                status = "Answered"

            answer_data.append([
                f"Q{question}",
                str(answer),
                status
            ])

        answer_table = Table(
            answer_data,
            colWidths=[
                1.5 * inch,
                2.6 * inch,
                2.7 * inch
            ],
            repeatRows=1
        )

        answer_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0),
                 colors.HexColor("#17365D")),

                ("TEXTCOLOR", (0, 0), (-1, 0),
                 colors.white),

                ("FONTNAME", (0, 0), (-1, 0),
                 "Helvetica-Bold"),

                ("FONTSIZE", (0, 0), (-1, -1), 8),

                ("GRID", (0, 0), (-1, -1), 0.4,
                 colors.HexColor("#CCCCCC")),

                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [
                     colors.white,
                     colors.HexColor("#F3F6FA")
                 ]),

                ("ALIGN", (0, 0), (-1, -1), "CENTER"),

                ("TOPPADDING", (0, 0), (-1, -1), 6),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
            ])
        )

        story.append(answer_table)

        story.append(Spacer(1, 20))

        # ----------------------------------
        # REPORT FOOTER
        # ----------------------------------

        story.append(
            HRFlowable(
                width="100%",
                thickness=0.7,
                color=colors.HexColor("#CCCCCC")
            )
        )

        story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                "Generated automatically by SmartOMR AI.",
                subtitle_style
            )
        )

        # ----------------------------------
        # BUILD PDF
        # ----------------------------------

        document.build(story)

        return {
            "success": True,
            "message": "Student result PDF generated successfully.",
            "file_path": str(output_path)
        }

    except Exception as error:

        return {
            "success": False,
            "message": str(error),
            "file_path": None
        }
