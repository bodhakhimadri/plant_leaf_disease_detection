# LeafCare

LeafCare is a Streamlit application for plant-leaf disease detection and crop-health insights. Upload a leaf image to receive a diagnosis, confidence score, treatment guidance, and an optional AI-generated report.

## Features

- Validates that an uploaded image contains a leaf before disease classification.
- Classifies 38 disease and healthy-leaf categories across apple, corn, grape, potato, and tomato crops.
- Supports a MobileNetV2 classifier with an optional EfficientNetB0 ensemble.
- Shows a unique **Field Trust Score** based on confidence, image focus/exposure, and ensemble agreement.
- Displays the top three likely diagnoses and retake-photo guidance.
- Provides disease information, organic treatment guidance, prediction history, dashboards, and location-based alerts.
- Supports Supabase authentication and optional Groq AI reports.

## Hybrid model

The app always works with the primary MobileNetV2 model. When `ai/models/efficientnet_disease_model.keras` exists, LeafCare blends its probabilities with MobileNetV2. If the optional model is missing, incompatible, or fails to load, the app safely uses MobileNetV2 alone.

Train the optional ensemble model with:

```bash
python ai/scripts/train_ensemble.py
```

The training script checks that its dataset class order matches `ai/models/class_names.json` before training.

## Setup

Prerequisites: Python 3.11, a Supabase project, and Node.js only when applying
Supabase migrations through the CLI.

```bash
python -m venv .venv
source .venv/Scripts/activate  # Git Bash on Windows
pip install -r requirements.txt
```

Create `.env` with the active Supabase project URL and anon/public key. The
Groq values are optional and are only needed for the AI report button.

```env
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=YOUR_SUPABASE_ANON_KEY
GROQ_API_KEY=YOUR_GROQ_API_KEY
GROQ_MODEL=llama-3.1-8b-instant
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
