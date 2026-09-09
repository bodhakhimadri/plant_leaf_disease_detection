import os
from functools import lru_cache

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


@lru_cache(maxsize=1)
def get_report_model():
    """Choose a text model that is available to the configured Groq project."""
    configured_model = os.getenv("GROQ_MODEL")
    available_models = {
        model.id for model in client.models.list().data
    }

    candidates = [
        configured_model,
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
    ]

    for model in candidates:
        if model and model in available_models:
            return model

    raise RuntimeError(
        "No supported Groq report model is available to this API key. "
        "Set GROQ_MODEL in .env to a model ID shown in Groq Console → Models."
    )


def generate_report(
        disease: str,
        confidence: float
):
    
    prompt = f"""
You are an agricultural expert.

Disease Detected:
{disease}

Model Confidence:
{confidence:.2f}%

Generate a professional report in markdown format.

Include:

# Disease Summary
- What is this disease?

# Symptoms
- Common symptoms

# Organic Treatment
- Natural remedies
- Organic sprays
- Compost or nutrient recommendations

# Prevention
- Best prevention practices

# Recovery Time
- Estimated recovery period

# Farmer Recommendations
- Immediate actions farmer should take

Keep response concise and practical.
"""

    try:

        response = client.chat.completions.create(
            model=get_report_model(),
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4
        )

        return response.choices[0].message.content

    except Exception as e:
        raise RuntimeError(f"Groq report generation failed: {e}") from e
