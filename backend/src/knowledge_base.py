"""Disease information lookup for model predictions."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_PATH = BASE_DIR / "ai" / "dataset" / "disease_knowledge.json"

with KNOWLEDGE_PATH.open("r", encoding="utf-8") as file:
    disease_db = json.load(file)


def get_disease_info(disease):
    """Always return the fields used by the UI, including for unlisted classes."""
    info = disease_db.get(disease)
    if not info:
        display_name = str(disease or "unknown class").replace("___", " — ").replace("_", " ")
        if str(disease or "").lower().endswith("healthy"):
            info = {
                "description": "No disease was identified in this leaf image.",
                "symptoms": ["No obvious disease symptoms; the leaf appears generally healthy."],
                "organic_treatment": ["No disease treatment is indicated; continue normal crop care."],
                "prevention": ["Monitor plants regularly and maintain good growing conditions."],
            }
        else:
            info = {
                "description": (
                    f"Detailed information for {display_name} is not yet in the local reference. "
                    "Use this prediction as a guide and confirm it with a local agricultural expert."
                ),
                "symptoms": [
                    "Compare the leaf with trusted crop guidance for spots, discoloration, curling, or wilting.",
                    "Seek expert confirmation if symptoms spread or the plant declines.",
                ],
                "organic_treatment": [
                    "Remove badly affected material when practical and clean tools after use.",
                    "Confirm the diagnosis before applying treatment; follow local crop-safe guidance.",
                ],
                "prevention": [
                    "Monitor plants regularly and avoid prolonged leaf wetness.",
                    "Clean tools after handling suspect plants.",
                ],
            }

    return {
        "description": info.get("description") or "Disease information is not available.",
        "symptoms": info.get("symptoms") or (
            ["No obvious disease symptoms; the leaf appears generally healthy."]
            if str(disease or "").lower().endswith("healthy")
            else ["Compare visible leaf changes with trusted local crop guidance."]
        ),
        "organic_treatment": info.get("organic_treatment") or [
            "Confirm the diagnosis before treatment and follow local crop-safe guidance."
        ],
        "prevention": info.get("prevention") or [
            "Monitor the crop regularly and clean tools after handling suspect plants."
        ],
    }
