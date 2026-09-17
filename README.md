# LeafCare

LeafCare is a Streamlit application for plant-leaf disease detection and crop-health insights. Upload a leaf image to receive a model prediction, confidence score, disease information, organic treatment guidance, and an optional AI-generated report.

It also provides secure user accounts, prediction history, dashboard analytics, and regional disease alerts powered by Supabase.

## Features

- Validates that an uploaded image contains a leaf before running disease classification.
- Classifies 38 plant disease and healthy-leaf categories across apple, corn, grape, potato, and tomato crops.
- Shows prediction confidence, symptoms, disease details, and organic treatment recommendations.
- Generates optional disease reports through Groq.
- Saves reports to each authenticated user's history.
- Displays personal and community crop-health analytics.
- Alerts users when disease-report thresholds are reached in their district.
- Stores authentication and location-aware profile data with Supabase.

## Technology

| Area | Tools |
| --- | --- |
| Web app | Streamlit |
| Machine learning | TensorFlow, Keras, MobileNetV2 |
| Image processing | Pillow, OpenCV, NumPy |
| Data and authentication | Supabase PostgreSQL and Supabase Auth |
| AI reports | Groq |
| Visualizations | Plotly |

## Hybrid model and Field Trust Score

LeafCare keeps MobileNetV2 as its primary classifier and can blend it with an
optional EfficientNetB0 model. The app falls back safely to MobileNetV2 when
the optional model has not been trained.

The unique **Field Trust Score** combines diagnosis confidence with real-world
photo focus and exposure. When the ensemble is enabled, it also includes the
agreement between both models. The result view displays the top three
diagnoses and actionable tips for a better field photo.

To train the optional EfficientNet model, run this from the repository root:

```bash
python ai/scripts/train_ensemble.py
```

Its dataset class order must match `ai/models/class_names.json`; the script
checks this before training to prevent unsafe prediction blending.

## Project structure

```text
.
|-- ai/                    # Models, datasets, and training scripts
|-- backend/src/           # Prediction, reports, analytics, and integrations
|-- supabase/migrations/   # Database schema and policies
|-- web/webapp/            # Streamlit pages and components
|-- app.py                 # Application entry point
|-- requirements.txt       # Python dependencies
`-- package.json           # Supabase CLI dependency
```

## Prerequisites

- Python 3.11
- A Supabase project
- A Groq API key if you want AI-generated reports
- Node.js and npm only if you want to apply Supabase migrations with the CLI

## Installation

Clone the repository and enter the project directory.

```bash
git clone https://github.com/Gobinda03/Plant_Disease_Detection.git
cd Plant_Disease_Detection
```

Create and activate a virtual environment.

```bash
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS or Linux
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies.

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the repository root. It is ignored by Git, so your credentials will not be committed.

```env
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=YOUR_SUPABASE_ANON_KEY

# Required only for AI-generated reports
GROQ_API_KEY=YOUR_GROQ_API_KEY

# Optional
GROQ_MODEL=llama-3.1-8b-instant
```

Find the Supabase URL and anon key in your Supabase project's **Connect** or **API** settings. Use the anon/public key, not a service-role key.

For a Streamlit deployment, configure the same values in `.streamlit/secrets.toml` instead:

```toml
SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
GROQ_MODEL = "llama-3.1-8b-instant"
```

## Supabase setup

Apply the included migrations to a Supabase project. With the Supabase CLI:

```bash
npm install
npx supabase login
npx supabase link --project-ref YOUR_PROJECT_REF
npx supabase db push
```

Alternatively, open the Supabase SQL Editor and execute the files in `supabase/migrations/` in filename order. The migrations create the schema, user-profile trigger, report policies, and supporting data required by LeafCare.

## Run the app

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit, typically `http://localhost:8501`.

## Troubleshooting

### Supabase URL is not found

Make sure `.env` exists in the project root and contains both `SUPABASE_URL` and `SUPABASE_KEY`. Restart Streamlit after changing environment variables.

### `public.user_profiles` cannot be found

Apply all SQL files in `supabase/migrations/`, in filename order, then retry the request.

### AI reports are unavailable

Set `GROQ_API_KEY` in `.env` or Streamlit secrets. Leaf detection and disease classification work without it; only report generation is disabled.

## License

No license text has been added to this repository yet. Add a license before distributing or reusing the project.
