"""Optional ensemble and field-photo reliability helpers for LeafCare.

The primary MobileNetV2 classifier remains the source of truth unless a
compatible EfficientNet model has been trained and saved locally.
"""

from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf


BASE_DIR = Path(__file__).resolve().parents[2]
ENSEMBLE_MODEL_PATH = BASE_DIR / "ai" / "models" / "efficientnet_disease_model.keras"
_ensemble_model = None
_ensemble_checked = False


def _get_ensemble_model():
    """Load the optional model once. Missing or invalid models are ignored."""
    global _ensemble_model, _ensemble_checked
    if not _ensemble_checked:
        _ensemble_checked = True
        if ENSEMBLE_MODEL_PATH.exists():
            try:
                _ensemble_model = tf.keras.models.load_model(ENSEMBLE_MODEL_PATH, compile=False)
            except Exception as error:
                print(f"Optional ensemble model was not loaded: {error}")
    return _ensemble_model


def blend_predictions(image_batch, primary_probabilities):
    """Blend equal-length class probabilities; otherwise preserve primary output."""
    model = _get_ensemble_model()
    if model is None:
        return primary_probabilities, None
    try:
        secondary = model.predict(image_batch, verbose=0)[0]
        if secondary.shape != primary_probabilities.shape:
            print("Optional ensemble model has incompatible output classes; using primary model.")
            return primary_probabilities, None
        agreement = float(np.minimum(primary_probabilities, secondary).sum() * 100)
        return (primary_probabilities + secondary) / 2, round(agreement, 2)
    except Exception as error:
        print(f"Ensemble prediction failed; using primary model: {error}")
        return primary_probabilities, None


def analyse_photo_quality(image_path):
    """Return a simple, explainable score for focus and exposure of a field photo."""
    image = cv2.imread(str(image_path))
    if image is None:
        return {"score": 0, "tips": ["Use a readable JPG or PNG image."]}
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(grayscale))
    focus = float(cv2.Laplacian(grayscale, cv2.CV_64F).var())
    exposure = max(0.0, 1.0 - abs(brightness - 130) / 130)
    focus_score = min(focus / 160, 1.0)
    score = round((exposure * 0.45 + focus_score * 0.55) * 100)
    tips = []
    if brightness < 60:
        tips.append("Use even daylight; this photo is too dark.")
    elif brightness > 215:
        tips.append("Avoid direct glare; this photo is overexposed.")
    if focus < 55:
        tips.append("Move closer and focus on the affected leaf before taking another photo.")
    return {"score": score, "tips": tips or ["Photo exposure and focus are suitable for analysis."]}


def field_trust_score(confidence, quality_score, agreement):
    """Reliability score that never pretends a one-model result is an ensemble."""
    if agreement is None:
        return round(0.75 * confidence + 0.25 * quality_score)
    return round(0.55 * confidence + 0.25 * quality_score + 0.20 * agreement)
