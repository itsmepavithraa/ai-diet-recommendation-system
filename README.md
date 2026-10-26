# AI Based Diet Recommendation System

Enter a Patient ID and get a complete report: diabetic retinopathy stage
(predicted by your real CNN model ahead of time), vitals, daily nutrition
targets, a personalized Indian diet plan, today's suggested meal plan, and
detailed control guidance. Nothing to upload, nothing to type except the ID.

## How the data was built

All 500 patient records were generated **for real**, not faked:

1. 577 retina images (your renamed dataset) were each run through your
   actual trained model, `diabetes_model.h5`, using the same CNN
   architecture as your original `predictor.py`.
2. The first 500 genuine predictions (severity level + confidence) became
   the backbone of each patient record.
3. Realistic vitals (age, gender, height, weight, BMI, glucose, blood
   pressure, insulin, activity level) were generated per patient, weighted
   so that more severe retinopathy stages correlate with worse metabolic
   vitals — mirroring real clinical patterns.
4. Daily calorie/macro targets were calculated with the same
   Mifflin-St Jeor + activity-factor formula as `macro_calc.py`.
5. A personalized Indian diet plan and detailed control recommendation
   were assigned per patient based on their predicted severity stage.

This is saved as `dataset/patients_500_dataset.csv` and loaded into MySQL.

## Folder structure

```text
AI_Diet_Recommendation_System/
  app.py                  Main Flask app
  db.py                   MySQL connection
  pdf_generator.py         Builds the saved PDF report
  requirements.txt
  dataset/
    patients_500_dataset.csv
    schema.sql              Run this in MySQL Workbench first
  scripts/
    seed_database.py        Loads the CSV into MySQL (run once)
  static/
    css/style.css
    retina_images/           500 retina images, one per patient
  templates/
    index.html
    report.html
    not_found.html
  saved_reports/            PDF reports get saved here when downloaded
```

## Setup

### 1. Create the database

Open MySQL Workbench, open `dataset/schema.sql`, select all, and execute it.
This creates the `diet_recommendation_db` database with two tables:
`patients` (the 500 pre-loaded records) and `food_items` (501 Indian dishes
used for the live "Today's Meal Plan" section).

### 2. Set your MySQL password

Open `db.py` and `scripts/seed_database.py`, and change `"password": "root"`
to your actual MySQL password.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Load the 500 patient records into MySQL

```bash
python scripts/seed_database.py
```

You should see: `Successfully inserted 500 patient records into MySQL.`

### 5. Run the app

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

Try Patient IDs P001 through P500 — the homepage also shows six random
sample IDs as quick links.

## Saving / printing a report

Each report page has two options:
- **Save PDF to saved_reports/** — generates a polished PDF and saves it
  directly into the `saved_reports/` folder inside this project, and also
  offers it as a browser download.
- **Print** — opens the browser's native print dialog for a quick paper
  copy or browser-side Save-as-PDF.
