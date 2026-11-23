"""Gemini-powered disease report generation with a local fallback."""

import json
import os
import time
from functools import lru_cache

import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
NON_TEXT_REPORT_MODEL_TERMS = (
    "tts", "audio", "image", "live", "embedding", "robotics", "computer-use",
)
TRANSIENT_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_GENERATION_ATTEMPTS = 2
GENERATION_TIMEOUT = (10, 75)
MAX_CANDIDATE_MODELS = 2


@lru_cache(maxsize=1)
def _available_models(api_key: str) -> list[str]:
    """Return models this API key advertises for content generation."""
    response = requests.get(
        GEMINI_API_BASE,
        headers={"x-goog-api-key": api_key},
        timeout=(10, 20),
    )
    response.raise_for_status()
    return [
        model["name"].removeprefix("models/")
        for model in response.json().get("models", [])
        if "generateContent" in model.get("supportedGenerationMethods", [])
    ]


def _candidate_models(api_key: str) -> list[str]:
    """Prefer fast text models and cap fallbacks to keep waits bounded."""
    available = [
        model for model in _available_models(api_key)
        if not any(term in model.lower() for term in NON_TEXT_REPORT_MODEL_TERMS)
    ]
    fast_models = sorted(
        (model for model in available if "flash" in model.lower()),
        key=lambda model: ("lite" not in model.lower(), model),
    )
    other_models = [model for model in available if model not in fast_models]
    return (fast_models + other_models)[:MAX_CANDIDATE_MODELS]


def _build_prompt(disease: str, confidence: float) -> str:
    return f"""Write a concise, plain-language Markdown crop-health report of about 100–130 words. Treat the prediction as decision support, not a confirmed diagnosis.

Detected disease: {disease}
Model confidence: {confidence:.2f}%

Use these headings in order: Summary and Resolution; Immediate Actions (next 24 hours); Common Symptoms; Organic Treatment; Prevention; Recovery and Monitoring.
Give three short numbered immediate actions. Keep advice crop-safe. Do not invent pesticide dosages, legal approvals, or guaranteed recovery times. Tell the farmer to consult a local agricultural expert if confidence is low or symptoms worsen."""


def _read_stream(response) -> str:
    """Read text chunks from Gemini's server-sent event response."""
    text_parts = []
    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue
        if isinstance(line, bytes):
            line = line.decode("utf-8", errors="replace")
        line = line.strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        chunk = json.loads(data)
        candidates = chunk.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            text_parts.extend(part.get("text", "") for part in parts)
    return "".join(text_parts).strip()


def _local_report(disease: str, confidence: float) -> str:
    """Build a report from the project's local disease reference."""
    from backend.src.knowledge_base import get_disease_info

    info = get_disease_info(disease) or {}
    description = info.get("description") or (
        f"The classifier identified {disease.replace('___', ' — ').replace('_', ' ')}. "
        "Confirm the result by comparing several leaves and consulting local guidance."
    )
    symptoms = info.get("symptoms") or [
        "Compare visible leaf changes with a trusted local disease reference."
    ]
    treatments = info.get("organic_treatment") or [
        "Avoid applying a treatment until the diagnosis is confirmed; follow local crop-safe guidance."
    ]
    prevention = info.get("prevention") or [
        "Monitor the crop regularly and clean tools after handling suspect plants."
    ]
    return "\n\n".join((
        f"## Summary and Resolution\n{description}",
        "## Immediate Actions (next 24 hours)\n"
        "1. Inspect several leaves and compare their symptoms.\n"
        "2. Remove badly affected material when practical.\n"
        "3. Ask a local agricultural expert to confirm low-confidence or worsening cases.",
        "## Common Symptoms\n" + "\n".join(f"- {item}" for item in symptoms),
        "## Organic Treatment\n" + "\n".join(f"- {item}" for item in treatments),
        "## Prevention\n" + "\n".join(f"- {item}" for item in prevention),
        "## Recovery and Monitoring\nMonitor new growth and check whether symptoms continue to spread. "
        f"The classifier confidence is {confidence:.1f}%; this is not a laboratory diagnosis.",
    ))


def generate_report(disease: str, confidence: float) -> str:
    """Return a Gemini report, or local guidance if Gemini is unreachable."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _local_report(disease, confidence)

    try:
        payload = {
            "contents": [{"parts": [{"text": _build_prompt(disease, confidence)}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 900},
        }
        models = _candidate_models(api_key)
        for model in models:
            for attempt in range(MAX_GENERATION_ATTEMPTS):
                try:
                    response = requests.post(
                        f"{GEMINI_API_BASE}/{model}:streamGenerateContent?alt=sse",
                        headers={
                            "x-goog-api-key": api_key,
                            "Content-Type": "application/json",
                        },
                        json=payload,
                        timeout=GENERATION_TIMEOUT,
                        stream=True,
                    )
                except requests.Timeout:
                    if attempt < MAX_GENERATION_ATTEMPTS - 1:
                        time.sleep(1)
                        continue
                    break

                if response.status_code in (400, 403, 404):
                    response.close()
                    break
                if response.status_code in TRANSIENT_STATUS_CODES:
                    response.close()
                    if attempt < MAX_GENERATION_ATTEMPTS - 1:
                        time.sleep(attempt + 1)
                        continue
                    break

                response.raise_for_status()
                try:
                    report = _read_stream(response)
                finally:
                    response.close()
                if report:
                    return report
                break
    except Exception:
        # Keep report generation useful during API, network, or key outages.
        pass

    return _local_report(disease, confidence)
