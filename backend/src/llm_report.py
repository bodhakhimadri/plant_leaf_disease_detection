"""Gemini-powered disease report generation."""

import os
import time
from functools import lru_cache

import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
NON_TEXT_REPORT_MODEL_TERMS = (
    "tts",
    "audio",
    "image",
    "live",
    "embedding",
    "robotics",
    "computer-use",
)
TRANSIENT_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_GENERATION_ATTEMPTS = 3


@lru_cache(maxsize=1)
def _available_models(api_key: str) -> list[str]:
    """Return models this API key may use for generateContent."""
    response = requests.get(
        GEMINI_API_BASE,
        headers={"x-goog-api-key": api_key},
        timeout=20,
    )
    response.raise_for_status()
    return [
        model["name"].removeprefix("models/")
        for model in response.json().get("models", [])
        if "generateContent" in model.get("supportedGenerationMethods", [])
    ]


def _candidate_models(api_key: str) -> list[str]:
    """Use only models advertised as usable by this API key."""
    available = _available_models(api_key)
    # Prefer fast text models when the API lists one, but do not hard-code a
    # version or model identifier that may be unavailable to this project.
    report_models = [
        model
        for model in available
        if not any(term in model.lower() for term in NON_TEXT_REPORT_MODEL_TERMS)
    ]
    flash_models = [model for model in report_models if "flash" in model.lower()]
    other_models = [model for model in report_models if model not in flash_models]
    return flash_models + other_models


def _build_prompt(disease: str, confidence: float) -> str:
    return f"""
You are an agricultural extension expert. Produce a concise, practical report
in Markdown for a farmer. This is decision support, not a laboratory diagnosis.

Detected disease: {disease}
Model confidence: {confidence:.2f}%

Use these headings in exactly this order:
# Summary and Resolution
# Immediate Actions (next 24 hours)
# Common Symptoms
# Organic Treatment
# Prevention
# Recovery and Monitoring

In **Summary and Resolution**, write two short paragraphs: first explain the
disease and its risk; then state the practical way to resolve or control it.
In **Immediate Actions**, give 3–5 numbered actions a farmer can take today.
Give actionable, crop-safe guidance. Clearly say that a low-confidence result
or worsening symptoms should be checked by a local agricultural expert. Do not
invent pesticide dosage, legal approvals, or a guaranteed recovery time.
""".strip()


def generate_report(disease: str, confidence: float) -> str:
    """Generate a report via Gemini with GEMINI_API_KEY from .env."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Gemini is not configured. Add GEMINI_API_KEY to .env and restart Streamlit."
        )

    try:
        payload = {
            "contents": [{"parts": [{"text": _build_prompt(disease, confidence)}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 900},
        }
        models = _candidate_models(api_key)
        if not models:
            raise RuntimeError(
                "This Gemini API key has no standard text model for report generation. "
                "Check Google AI Studio → API keys and project access."
            )

        unavailable_models = []
        transient_models = []
        for model in models:
            for attempt in range(MAX_GENERATION_ATTEMPTS):
                response = requests.post(
                    f"{GEMINI_API_BASE}/{model}:generateContent",
                    headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                    json=payload,
                    timeout=45,
                )
                if response.status_code == 404:
                    unavailable_models.append(model)
                    break
                if response.status_code in TRANSIENT_STATUS_CODES:
                    if attempt < MAX_GENERATION_ATTEMPTS - 1:
                        time.sleep(1.5 * (attempt + 1))
                        continue
                    transient_models.append(model)
                    break
                response.raise_for_status()
                data = response.json()
                parts = data["candidates"][0]["content"]["parts"]
                report = "".join(part.get("text", "") for part in parts).strip()
                if report:
                    return report
                raise ValueError("Gemini returned no report text")

        if transient_models:
            raise RuntimeError(
                "Gemini is temporarily unavailable after automatic retries. "
                "Please try generating the report again in a minute."
            )
        raise RuntimeError(
            "Gemini listed models but none accepted a report request: "
            + ", ".join(unavailable_models)
        )
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as error:
        raise RuntimeError(f"Gemini report generation failed: {error}") from error
