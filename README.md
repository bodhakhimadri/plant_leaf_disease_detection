# LeafCare

LeafCare is a Streamlit application for plant-leaf disease detection and crop-health insights. Upload a leaf image to receive a diagnosis, confidence score, treatment guidance, and an optional AI-generated report.

## Features

- Validates that an uploaded image contains a leaf before disease classification.
- Classifies 38 disease and healthy-leaf categories across apple, corn, grape, potato, and tomato crops.
- Uses a single DenseNet121 classifier fine-tuned from ImageNet weights.
- Shows a **Field Trust Score** based on diagnosis confidence and image focus/exposure.
- Displays the top three likely diagnoses and retake-photo guidance.
- Provides disease information, organic treatment guidance, prediction history, dashboards, and location-based alerts.
- Supports Supabase authentication and optional Gemini AI reports.

## DenseNet121 model

The disease classifier uses DenseNet121 only. Before starting the app for the
first time on this branch, train and save its ImageNet-initialized classifier:

```bash
python ai/scripts/train.py
```

Training writes `ai/models/densenet121_plant_disease.keras`, which the app loads
for predictions. The script verifies the class order against
`ai/models/class_names.json` and uses the local `ai/dataset/train` directory.

## Setup

Prerequisites: Python 3.11, a Supabase project, and Node.js only when applying
Supabase migrations through the CLI.

```bash
python -m venv .venv
source .venv/Scripts/activate  # Git Bash on Windows
pip install -r requirements.txt
```

Create `.env` with the active Supabase project URL and anon/public key. The
Gemini values are optional and are only needed for the AI report button.

```env
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=YOUR_SUPABASE_ANON_KEY
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Apply the provided Supabase migrations before using authentication and reports.
Use only the project reference (the subdomain before `.supabase.co`) with the
link command:

```bash
npx supabase link --project-ref YOUR_PROJECT_REF
npx supabase db push
```

Start the app:

```bash
streamlit run app.py
```

## Troubleshooting

If login shows a hostname or `getaddrinfo` error, check that `SUPABASE_URL`
uses the active URL from Supabase Dashboard and restart Streamlit after editing
`.env`. A new Supabase project has an empty authentication database, so register
a new user before attempting to log in.
