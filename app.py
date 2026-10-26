# AI Based Diet Recommendation System
#
# Enter a Patient ID -> get the complete pre-loaded report: name, age,
# vitals, retina image, diabetic retinopathy stage (predicted by the real
# diabetes_model.h5 CNN ahead of time on 500 real retina images),
# nutrition targets, a personalized Indian diet plan, a live "today's
# meal plan" pulled from the food_items table, and detailed guidance.
#
# All 500 patient records are pre-loaded into MySQL via scripts/seed_database.py
# from dataset/patients_500_dataset.csv — no live uploads, no manual entry,
# matching the "enter ID only" requirement.

import os
import random
from flask import Flask, render_template, request, send_file, abort
from db import get_connection
from pdf_generator import generate_report_pdf

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RETINA_IMAGES_DIR = os.path.join(BASE_DIR, "static", "retina_images")
SAVED_REPORTS_DIR = os.path.join(BASE_DIR, "saved_reports")
os.makedirs(SAVED_REPORTS_DIR, exist_ok=True)


def get_patient(patient_id):
    patient_id = patient_id.strip().upper()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
    patient = cursor.fetchone()
    cursor.close()
    conn.close()
    return patient


def get_meal_plan(dr_stage):
    """Pulls one randomized food item per meal type, matching the patient's
    dietary suitability (diabetic-friendly foods for any DR stage above None)."""
    food_filter = "diabetic" if dr_stage != "No DR" else "all"

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    meal_plan = {}
    for meal in ["Breakfast", "Lunch", "Snacks", "Dinner"]:
        cursor.execute("""
            SELECT * FROM food_items
            WHERE meal_type = %s
            AND (suitable_for = %s OR suitable_for = 'all')
            ORDER BY RAND()
            LIMIT 1
        """, (meal, food_filter))
        meal_plan[meal] = cursor.fetchone()

    cursor.close()
    conn.close()
    return meal_plan


def dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM patients")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS high_risk FROM patients WHERE dr_severity IN ('High Risk', 'Very High Risk')")
    high_risk = cursor.fetchone()["high_risk"]

    cursor.execute("SELECT AVG(calories_kcal) AS avg_cal FROM patients")
    avg_row = cursor.fetchone()
    avg_calories = int(avg_row["avg_cal"]) if avg_row["avg_cal"] else 0

    cursor.execute("SELECT patient_id FROM patients ORDER BY RAND() LIMIT 6")
    sample_ids = [row["patient_id"] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return {
        "patients": total,
        "high_risk": high_risk,
        "avg_calories": avg_calories,
        "sample_ids": sample_ids,
    }


def severity_class(severity):
    mapping = {
        "Low Risk": "good",
        "Low-Medium Risk": "medium-low",
        "Medium Risk": "medium",
        "High Risk": "warning",
        "Very High Risk": "danger",
    }
    return mapping.get(severity, "good")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        patient_id = request.form.get("patient_id", "").strip().upper()
        if patient_id:
            return report(patient_id)

    return render_template("index.html", stats=dashboard_stats())


@app.route("/report/<patient_id>")
def report(patient_id):
    patient = get_patient(patient_id)
    if patient is None:
        return render_template("not_found.html", patient_id=patient_id.upper()), 404

    meal_plan = get_meal_plan(patient["dr_stage"])

    return render_template(
        "report.html",
        patient=patient,
        meal_plan=meal_plan,
        severity_class=severity_class(patient["dr_severity"]),
    )


@app.route("/report/<patient_id>/download")
def download_report(patient_id):
    patient = get_patient(patient_id)
    if patient is None:
        abort(404)

    # Use a fresh meal plan for the PDF snapshot too
    patient["meal_plan"] = get_meal_plan(patient["dr_stage"])

    retina_path = os.path.join(RETINA_IMAGES_DIR, patient["retina_image"] or "")
    filepath, filename = generate_report_pdf(patient, retina_path, SAVED_REPORTS_DIR)

    return send_file(filepath, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(debug=True)
