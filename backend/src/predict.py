"""Hybrid disease prediction with quality-aware confidence reporting."""

import json
from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf

from ai.leaf_validation.leaf_predict import is_leaf
from backend.src.logger import log_event
from backend.src.hybrid import (
    analyse_photo_quality,
    blend_predictions,
    field_trust_score,
)

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "ai" / "models" / "trained_plant_disease_model.keras"
ENSEMBLE_MODEL_PATH = BASE_DIR / "ai" / "models" / "efficientnet_disease_model.keras"
CLASS_NAMES_PATH = BASE_DIR / "ai" / "models" / "class_names.json"
IMAGE_SIZE = (128, 128)


def _load_model(path: Path, required: bool = False):
    """Load an optional model without preventing the app from starting."""
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Required model not found: {path}")
        return None
    return tf.keras.models.load_model(path, compile=False)


primary_model = _load_model(MODEL_PATH, required=True)
ensemble_model = _load_model(ENSEMBLE_MODEL_PATH)
with CLASS_NAMES_PATH.open("r", encoding="utf-8") as file:
    CLASS_NAMES = json.load(file)


def _prepare_image(image_path: str) -> np.ndarray:
    image = tf.keras.preprocessing.image.load_img(image_path, target_size=IMAGE_SIZE)
    array = tf.keras.preprocessing.image.img_to_array(image)
    return np.expand_dims(array, axis=0)


def _photo_quality(image_path: str) -> dict:
    """Score practical field-photo quality: brightness, focus and leaf coverage."""
    image = cv2.imread(str(image_path))
    if image is None:
        return {"score": 0, "notes": ["Image could not be read."]}
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, (25, 25, 20), (95, 255, 255))
    green_coverage = float(np.mean(green_mask > 0))
    brightness_score = max(0.0, 1.0 - abs(brightness - 135.0) / 135.0)
    sharpness_score = min(sharpness / 180.0, 1.0)
    coverage_score = min(green_coverage / 0.25, 1.0)
    score = round(100 * (0.35 * brightness_score + 0.40 * sharpness_score + 0.25 * coverage_score))
    notes = []
    if brightness < 55:
        notes.append("The image is too dark; photograph the leaf in even daylight.")
    elif brightness > 215:
        notes.append("The image is overexposed; avoid direct glare on the leaf.")
    if sharpness < 60:
        notes.append("The image is blurry; hold the camera steady and focus on the lesion.")
    if green_coverage < 0.08:
        notes.append("Keep one leaf large and centred in the frame.")
    return {"score": score, "notes": notes or ["Photo quality is suitable for analysis."]}


def _top_predictions(probabilities: np.ndarray, count: int = 3) -> list[dict]:
    indices = np.argsort(probabilities)[-count:][::-1]
    return [
        {"disease": CLASS_NAMES[int(index)], "confidence": round(float(probabilities[index] * 100), 2)}
        for index in indices
    ]


def _trust_score(confidence: float, quality_score: int, agreement: float, model_count: int) -> int:
    """Field Trust Score combines visual certainty, photo quality and model agreement."""
    if model_count == 1:
        return round(0.75 * confidence + 0.25 * quality_score)
    return round(0.55 * confidence + 0.25 * quality_score + 0.20 * agreement)


def predict_disease(image_path: str) -> dict:
    leaf, leaf_confidence = is_leaf(image_path)
    if not leaf:
<<<<<<< Updated upstream
        return {
            "success": False,
            "message": "Please upload a clear image of a plant leaf.",
            "leaf_confidence": round(leaf_confidence, 2)
        }

    # Load image
    img = tf.keras.preprocessing.image.load_img(
        image_path,
        target_size=(128, 128)
    )

    img_array = tf.keras.preprocessing.image.img_to_array(img)

    img_array = np.expand_dims(img_array, axis=0)

    primary_prediction = model.predict(img_array, verbose=0)[0]
    prediction, agreement = blend_predictions(img_array, primary_prediction)

    predicted_index = int(np.argmax(prediction))
    confidence = float(prediction[predicted_index] * 100)

    disease = CLASS_NAMES[predicted_index]

    # Print Top-5 predictions for debugging
    print("\n========== Prediction ==========")
    top5 = np.argsort(prediction)[-5:][::-1]

    for idx in top5:
        print(
            f"{CLASS_NAMES[idx]} : {prediction[idx] * 100:.2f}%"
        )

    print("Predicted:", disease)
    print("Confidence:", confidence)
    print("================================\n")

    log_event(
        "DISEASE DETECTED",
        {
            "disease": disease,
            "confidence": round(confidence, 2)
        }
    )

    top_indices = np.argsort(prediction)[-3:][::-1]
    photo_quality = analyse_photo_quality(image_path)

    return {
        "success": True,
        "disease": disease,
        "confidence": confidence,
        "top_predictions": [
            {
                "disease": CLASS_NAMES[int(index)],
                "confidence": round(float(prediction[index] * 100), 2),
            }
            for index in top_indices
        ],
        "photo_quality": photo_quality,
        "model_agreement": agreement,
        "field_trust_score": field_trust_score(
            confidence, photo_quality["score"], agreement
        ),
=======
        return {"success": False, "message": "Please upload a clear image of a plant leaf.", "leaf_confidence": round(leaf_confidence, 2)}
    image = _prepare_image(image_path)
    primary_probabilities = primary_model.predict(image, verbose=0)[0]
    model_count, agreement = 1, 100.0
    if ensemble_model is not None:
        ensemble_probabilities = ensemble_model.predict(image, verbose=0)[0]
        if len(ensemble_probabilities) == len(primary_probabilities):
            model_count = 2
            agreement = float(np.sum(np.minimum(primary_probabilities, ensemble_probabilities)) * 100)
            probabilities = 0.5 * primary_probabilities + 0.5 * ensemble_probabilities
        else:
            probabilities = primary_probabilities
    else:
        probabilities = primary_probabilities
    prediction_index = int(np.argmax(probabilities))
    confidence = float(probabilities[prediction_index] * 100)
    quality = _photo_quality(image_path)
    trust_score = _trust_score(confidence, quality["score"], agreement, model_count)
    disease = CLASS_NAMES[prediction_index]
    log_event("DISEASE DETECTED", {"disease": disease, "confidence": round(confidence, 2), "field_trust_score": trust_score, "models_used": model_count})
    return {
        "success": True, "disease": disease, "confidence": round(confidence, 2),
        "top_predictions": _top_predictions(probabilities), "photo_quality": quality,
        "field_trust_score": trust_score, "model_agreement": round(agreement, 2) if model_count == 2 else None,
        "models_used": model_count, "ensemble_available": ensemble_model is not None,
>>>>>>> Stashed changes
    }
