"""Disease information lookup with a safe fallback for unlisted classes."""

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_PATH = BASE_DIR / "ai" / "dataset" / "disease_knowledge.json"

with KNOWLEDGE_PATH.open("r", encoding="utf-8") as file:
    disease_db = json.load(file)


def get_disease_info(disease):
    """Return curated information, or cautious generic advice if not listed."""
    info = disease_db.get(disease)
    if info is not None:
        return info

    display_name = str(disease).replace("___", " — ").replace("_", " ")
    return {
        "description": (
            f"Detailed guidance for {display_name} is not yet in the local "
            "disease reference. Confirm the diagnosis with a local agricultural expert."
        ),
        "symptoms": [
            "Symptoms vary by crop and disease. Compare the leaf with trusted local guidance.",
            "If symptoms spread or the plant declines, seek help from an agricultural extension service.",
        ],
        "organic_treatment": [
            "Remove badly affected plant material when practical and clean tools after use.",
            "Avoid applying treatments until the disease is confirmed; follow local crop-safe guidance.",
        ],
    }
