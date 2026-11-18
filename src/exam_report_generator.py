
from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
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


def generate_exam_results_pdf(
    results,
    exam_name,
    output_path=None
):
    """
    Generate a complete examination results PDF.

    Parameters:
        results: List of saved student result dictionaries.
        exam_name: Name of the examination.
        output_path: Optional output PDF path.

    Returns:
        Dictionary containing success status and file path.
    """

    try:

        create_required_directories()

        if not results:
            raise ValueError("No examination results available.")

        if output_path is None:

            output_path = (
                Path(REPORT_DIR)
                / "exam_results_report.pdf"
            )

        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # ----------------------------------
        # CALCULATE PERFORMANCE
        # ----------------------------------

        total_students = len(results)

        average_percentage = sum(
            float(r["percentage"]) for r in results
        ) / total_students

        highest_percentage = max(
            float(r["percentage"]) for r in results
        )

        average_score = sum(
            float(r["score"]) for r in results
        ) / total_students

        # ----------------------------------
        # CREATE PDF DOCUMENT
        # ----------------------------------

        document = SimpleDocTemplate(
            str(output_path),
            pagesize=landscape(A4),
            rightMargin=0.45 * inch,
            leftMargin=0.45 * inch,
            topMargin=0.45 * inch,
            bottomMargin=0.45 * inch
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ExamTitle",
            parent=styles["Title"],
            fontSize=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17365D"),
            spaceAfter=8
        )

        subtitle_style = ParagraphStyle(
            "ExamSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=12
        )

        heading_style = ParagraphStyle(
            "ExamHeading",
            parent=styles["Heading2"],
            fontSize=12,
            textColor=colors.HexColor("#17365D"),
            spaceBefore=12,
            spaceAfter=8
        )

        story = []

        # ----------------------------------
        # REPORT HEADER
        # ----------------------------------

        story.append(
            Paragraph("SMARTOMR AI", title_style)
        )

        story.append(
            Paragraph(
                "EXAMINATION PERFORMANCE REPORT",
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

        story.append(Spacer(1, 12))

        story.append(
            Paragraph(
                f"<b>Examination:</b> {exam_name}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Report Generated:</b> "
                f"{datetime.now().strftime('%d-%m-%Y %I:%M %p')}",
                styles["Normal"]
            )
        )

        # ----------------------------------
        # PERFORMANCE SUMMARY
        # ----------------------------------

        story.append(
            Paragraph(
                "1. Examination Performance Summary",
                heading_style
            )
        )

        summary_data = [
            ["Total Students", "Average Score",
             "Average Percentage", "Highest Percentage"],

            [
                str(total_students),
                f"{average_score:.2f}",
                f"{average_percentage:.2f}%",
                f"{highest_percentage:.2f}%"
            ]
        ]

        summary_table = Table(
            summary_data,
            colWidths=[
                2 * inch,
                2 * inch,
                2.3 * inch,
                2.3 * inch
            ]
        )

        summary_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0),
                 colors.HexColor("#17365D")),

                ("TEXTCOLOR", (0, 0), (-1, 0),
                 colors.white),

                ("FONTNAME", (0, 0), (-1, 0),
                 "Helvetica-Bold"),

                ("FONTSIZE", (0, 0), (-1, -1), 9),

                ("ALIGN", (0, 0), (-1, -1), "CENTER"),

                ("GRID", (0, 0), (-1, -1), 0.5,
                 colors.grey),

                ("TOPPADDING", (0, 0), (-1, -1), 9),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 9)
            ])
        )

        story.append(summary_table)

        # ----------------------------------
        # STUDENT-WISE RESULTS
        # ----------------------------------

        story.append(
            Paragraph(
                "2. Student-wise Examination Results",
                heading_style
            )
        )

        table_data = [
            [
                "Roll Number",
                "Student Name",
                "Correct",
                "Incorrect",
                "Unanswered",
                "Review",
                "Score",
                "Maximum",
                "Percentage"
            ]
        ]

        sorted_results = sorted(
            results,
            key=lambda r: float(r["percentage"]),
            reverse=True
        )

        for result in sorted_results:

            table_data.append([
                str(result["roll_number"]),
                str(result["student_name"]),
                str(result["correct"]),
                str(result["incorrect"]),
                str(result["unanswered"]),
                str(result["review_required"]),
                str(result["score"]),
                str(result["maximum_marks"]),
                f"{float(result['percentage']):.2f}%"
            ])

        results_table = Table(
            table_data,
            repeatRows=1,
            colWidths=[
                0.9 * inch,
                1.35 * inch,
                0.65 * inch,
                0.65 * inch,
                0.75 * inch,
                0.55 * inch,
                0.65 * inch,
                0.65 * inch,
                0.8 * inch
            ]
        )

        results_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0),
                 colors.HexColor("#17365D")),

                ("TEXTCOLOR", (0, 0), (-1, 0),
                 colors.white),

                ("FONTNAME", (0, 0), (-1, 0),
                 "Helvetica-Bold"),

                ("FONTSIZE", (0, 0), (-1, -1), 8),

                ("GRID", (0, 0), (-1, -1), 0.4,
                 colors.grey),

                ("ALIGN", (2, 0), (-1, -1), "CENTER"),

                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [
                     colors.white,
                     colors.HexColor("#F3F6FA")
                 ]),

                ("TOPPADDING", (0, 0), (-1, -1), 7),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
            ])
        )

        story.append(results_table)

        story.append(Spacer(1, 18))

        story.append(
            HRFlowable(
                width="100%",
                thickness=0.7,
                color=colors.grey
            )
        )

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
            "message": "Examination PDF report generated successfully.",
            "file_path": str(output_path)
        }

    except Exception as error:

        return {
            "success": False,
            "message": str(error),
            "file_path": None
        }
