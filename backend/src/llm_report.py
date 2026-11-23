"""Gemini-powered disease report generation."""

import os
import time
import json
from functools import lru_cache

import requests
from dotenv import load_dotenv
from backend.src.knowledge_base import get_disease_info

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
GENERATION_TIMEOUT = (10, 75)


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
You are an agricultural extension expert. Write a concise, plain-language
Markdown report for a farmer, about 100–130 words. This is decision support,
not a laboratory diagnosis.

Detected disease: {disease}
Model confidence: {confidence:.2f}%

Use these headings in order. Keep each section brief:
# Summary and Resolution
# Immediate Actions (next 24 hours)
# Common Symptoms
# Organic Treatment
# Prevention
# Recovery and Monitoring

In **Summary and Resolution**, explain the risk and practical response. In
**Immediate Actions**, give three short numbered steps. Keep guidance concise.
Give actionable, crop-safe guidance. Clearly say that a low-confidence result
or worsening symptoms should be checked by a local agricultural expert. Do not
invent pesticide dosage, legal approvals, or a guaranteed recovery time.
""".strip()


def _stream_report(response) -> str:
    """Collect text parts from Gemini's server-sent event response."""
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
        if not candidates:
            continue
        parts = candidates[0].get("content", {}).get("parts", [])
        text_parts.extend(part.get("text", "") for part in parts)
    return "".join(text_parts).strip()


def _local_report(disease: str, confidence: float) -> str:
    """Build a safe report from the project's reviewed disease guidance."""
    info = get_disease_info(disease)
    symptoms = info.get("symptoms") or ["No curated symptoms are available; compare the leaf with a local expert's diagnosis."]
    treatment = info.get("organic_treatment") or ["Remove badly affected material where practical and seek local agricultural advice."]
    prevention = info.get("prevention") or ["Monitor plants regularly and avoid spreading suspect plant material."]
    return "\n\n".join((
        "## Summary and Resolution\n" + info.get("description", "Use this result as decision support, not a confirmed diagnosis."),
        "## Immediate Actions (next 24 hours)\n1. Inspect several leaves and compare symptoms.\n2. Remove badly affected material if practical.\n3. Ask a local agricultural expert to confirm low-confidence or worsening cases.",
        "## Common Symptoms\n" + "\n".join(f"- {item}" for item in symptoms),
        "## Organic Treatment\n" + "\n".join(f"- {item}" for item in treatment),
        "## Prevention\n" + "\n".join(f"- {item}" for item in prevention),
        "## Recovery and Monitoring\nMonitor new growth and check whether symptoms continue to spread. The classifier confidence is "
        f"{confidence:.1f}%; it is not a laboratory diagnosis.",
    ))


def generate_report(disease: str, confidence: float) -> dict[str, str]:
    """Use Gemini when available; otherwise return a clearly labeled local report."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"text": _local_report(disease, confidence), "source": "local",
                "notice": "Gemini is not configured. Add GEMINI_API_KEY to the project .env file and restart Streamlit."}

    try:
        payload = {
            "contents": [{"parts": [{"text": _build_prompt(disease, confidence)}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 900},
        }
        # Cap fallback attempts so a single button click does not wait through
        # every model advertised by the project.
        models = _candidate_models(api_key)[:2]
        if not models:
            raise RuntimeError(
                "This Gemini API key has no standard text model for report generation. "
                "Check Google AI Studio → API keys and project access."
            )

        unavailable_models = []
        transient_models = []
        rejected_models = []
        for model in models:
            for attempt in range(MAX_GENERATION_ATTEMPTS):
                try:
                    response = requests.post(
                        f"{GEMINI_API_BASE}/{model}:streamGenerateContent?alt=sse",
                        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                        json=payload,
                        timeout=GENERATION_TIMEOUT,
                        stream=True,
                    )
                except requests.Timeout:
                    if attempt < MAX_GENERATION_ATTEMPTS - 1:
                        time.sleep(attempt + 1)
                        continue
                    transient_models.append(model)
                    break
                # Model availability can differ from the models list. Try the
                # remaining advertised text models when one rejects generation.
                if response.status_code in (400, 403, 404):
                    response.close()
                    unavailable_models.append(model)
                    rejected_models.append(response.text[:500])
                    break
                if response.status_code in TRANSIENT_STATUS_CODES:
                    response.close()
                    if attempt < MAX_GENERATION_ATTEMPTS - 1:
                        time.sleep(1.5 * (attempt + 1))
                        continue
                    transient_models.append(model)
                    break
                response.raise_for_status()
                report = _stream_report(response)
                response.close()
                if report:
                    return {"text": report, "source": "Gemini", "notice": ""}
                raise ValueError("Gemini returned no report text")

        if transient_models:
            raise RuntimeError(
                "Gemini is temporarily unavailable after automatic retries. "
                "Please try generating the report again in a minute."
            )
        if rejected_models:
            details = rejected_models[-1]
            raise RuntimeError(
                "Gemini rejected every available text model. Check that the API "
                "key is valid, Gemini API access is enabled for its project, "
                f"and the project can use a listed model. Last response: {details}"
            )
        raise RuntimeError(
            "Gemini listed models but none accepted a report request: "
            + ", ".join(unavailable_models)
        )
    except Exception as error:
        return {
            "text": _local_report(disease, confidence),
            "source": "local",
            "notice": f"Gemini could not complete this request ({error}). Showing the report from the local disease guide instead.",
        }
