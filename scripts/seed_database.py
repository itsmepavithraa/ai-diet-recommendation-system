# Run this ONCE to load the 500 pre-defined patient records (generated using
# the real diabetes_model.h5 CNN on actual retina images) into MySQL.
#
# Usage:
#   1. Make sure MySQL is running and you've already run dataset/schema.sql
#      in MySQL Workbench to create the `diet_recommendation_db` database
#      and `patients` table.
#   2. Update DB_CONFIG below with your MySQL password.
#   3. Run:  python scripts/seed_database.py

import csv
import os
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",   # <-- change this to your MySQL password
    "database": "diet_recommendation_db",
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "dataset", "patients_500_dataset.csv")


def main():
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: CSV not found at {CSV_PATH}")
        return

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Clear existing data so this script is safe to re-run
    cursor.execute("DELETE FROM patients")
    conn.commit()

    inserted = 0
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""
                INSERT INTO patients
                (patient_id, full_name, age, gender, height_cm, weight_kg, bmi,
                 glucose_mg, blood_pressure, insulin_mu, activity_level, retina_image,
                 dr_stage, dr_severity, confidence, calories_kcal, protein_g, carbs_g,
                 fat_g, diet_plan, recommendation, detailed_guidance)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row["patient_id"], row["full_name"], int(row["age"]), row["gender"],
                float(row["height_cm"]), float(row["weight_kg"]), float(row["bmi"]),
                int(row["glucose_mg"]), row["blood_pressure"], int(row["insulin_mu"]),
                row["activity_level"], row["retina_image"], row["dr_stage"],
                row["dr_severity"], float(row["confidence"]), int(row["calories_kcal"]),
                int(row["protein_g"]), int(row["carbs_g"]), int(row["fat_g"]),
                row["diet_plan"], row["recommendation"], row["detailed_guidance"]
            ))
            inserted += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Successfully inserted {inserted} patient records into MySQL.")


if __name__ == "__main__":
    main()
