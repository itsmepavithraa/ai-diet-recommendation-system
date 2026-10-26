# Generates a saved PDF copy of a patient's report using reportlab.
# Called by the /report/<patient_id>/download route in app.py.
# Saved PDFs go into the saved_reports/ folder so the user can find
# them later without relying on the browser's print dialog.

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
)

SEVERITY_COLORS = {
    "Low Risk": colors.HexColor("#2e7d32"),
    "Low-Medium Risk": colors.HexColor("#f57f17"),
    "Medium Risk": colors.HexColor("#e65100"),
    "High Risk": colors.HexColor("#c62828"),
    "Very High Risk": colors.HexColor("#b71c1c"),
}


def generate_report_pdf(patient, retina_image_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Report_{patient['patient_id']}_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                             topMargin=18 * mm, bottomMargin=18 * mm,
                             leftMargin=18 * mm, rightMargin=18 * mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=22, spaceAfter=2)
    sub_style = ParagraphStyle("SubStyle", parent=styles["Normal"], textColor=colors.grey, fontSize=10)
    h2_style = ParagraphStyle("H2Style", parent=styles["Heading2"], fontSize=13, spaceBefore=14, spaceAfter=6,
                               textColor=colors.HexColor("#0d47a1"))
    body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontSize=10.5, leading=15)

    elements = []

    elements.append(Paragraph("Personalized Health Report", sub_style))
    elements.append(Paragraph(patient["full_name"], title_style))
    elements.append(Paragraph(f"Patient ID: {patient['patient_id']}", sub_style))
    elements.append(Spacer(1, 10))

    # Retina image + DR stage side by side
    severity_color = SEVERITY_COLORS.get(patient["dr_severity"], colors.grey)
    if os.path.exists(retina_image_path):
        img = RLImage(retina_image_path, width=55 * mm, height=55 * mm)
    else:
        img = Paragraph("Retina image not found", body_style)

    dr_info = [
        [Paragraph(f"<b>Diabetic Retinopathy Stage</b>", body_style)],
        [Paragraph(f"<font size=16 color='{severity_color.hexval()}'><b>{patient['dr_stage']}</b></font>", body_style)],
        [Paragraph(f"Risk Level: <b>{patient['dr_severity']}</b> &nbsp;|&nbsp; Model Confidence: <b>{patient['confidence']}%</b>", body_style)],
    ]
    dr_table = Table(dr_info, colWidths=[100 * mm])
    dr_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e3f2fd")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#90caf9")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    top_row = Table([[img, dr_table]], colWidths=[60 * mm, 110 * mm])
    top_row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    elements.append(top_row)
    elements.append(Spacer(1, 14))

    # Patient details + Nutrition targets
    elements.append(Paragraph("Patient Details", h2_style))
    details_data = [
        ["Age", str(patient["age"]), "Gender", patient["gender"]],
        ["Height", f"{patient['height_cm']} cm", "Weight", f"{patient['weight_kg']} kg"],
        ["BMI", str(patient["bmi"]), "Activity Level", patient["activity_level"]],
        ["Blood Pressure", f"{patient['blood_pressure']} mmHg", "Glucose", f"{patient['glucose_mg']} mg/dL"],
        ["Insulin", f"{patient['insulin_mu']} mu/L", "", ""],
    ]
    details_table = Table(details_data, colWidths=[35 * mm, 50 * mm, 35 * mm, 50 * mm])
    details_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f5f5f5")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f5f5f5")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(details_table)

    elements.append(Paragraph("Daily Nutrition Targets", h2_style))
    nutrition_data = [
        ["Calories", f"{patient['calories_kcal']} kcal/day"],
        ["Protein", f"{patient['protein_g']} g/day"],
        ["Carbohydrates", f"{patient['carbs_g']} g/day"],
        ["Fat", f"{patient['fat_g']} g/day"],
    ]
    nutrition_table = Table(nutrition_data, colWidths=[60 * mm, 60 * mm])
    nutrition_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8f5e9")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(nutrition_table)

    # Diet plan
    elements.append(Paragraph("Personalized Indian Diet Plan (Sample)", h2_style))
    diet_items = [d.strip() for d in patient["diet_plan"].split(";") if d.strip()]
    diet_data = [[Paragraph(item, body_style)] for item in diet_items]
    diet_table = Table(diet_data, colWidths=[170 * mm])
    diet_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fafafa")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(diet_table)

    # Today's meal plan (from live food_items query, passed in patient dict)
    if patient.get("meal_plan"):
        elements.append(Paragraph("Today's Suggested Meal Plan", h2_style))
        meal_rows = []
        for meal_name, food in patient["meal_plan"].items():
            if food:
                meal_rows.append([
                    Paragraph(f"<b>{meal_name}</b>", body_style),
                    Paragraph(f"{food['food_name']} — {food['calories']} kcal, "
                              f"C:{food['carbs_g']}g P:{food['protein_g']}g F:{food['fat_g']}g", body_style)
                ])
        if meal_rows:
            meal_table = Table(meal_rows, colWidths=[30 * mm, 140 * mm])
            meal_table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dddddd")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elements.append(meal_table)

    # Recommendation
    elements.append(Paragraph("Final Recommendation", h2_style))
    elements.append(Paragraph(f"<b>{patient['recommendation']}</b>", body_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(patient["detailed_guidance"], body_style))

    elements.append(Spacer(1, 16))
    elements.append(Paragraph(
        f"Report generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    ))

    doc.build(elements)
    return filepath, filename
