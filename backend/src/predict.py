"""Disease prediction with an optional EfficientNet ensemble."""

import json
from pathlib import Path

import numpy as np
import tensorflow as tf

from ai.leaf_validation.leaf_predict import is_leaf
from backend.src.hybrid import analyse_photo_quality, blend_predictions, field_trust_score
from backend.src.logger import log_event

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "ai" / "models" / "trained_plant_disease_model.keras"
CLASS_NAMES_PATH = BASE_DIR / "ai" / "models" / "class_names.json"
IMAGE_SIZE = (128, 128)

model = tf.keras.models.load_model(MODEL_PATH, compile=False)
with CLASS_NAMES_PATH.open("r", encoding="utf-8") as file:
    CLASS_NAMES = json.load(file)


def _top_predictions(probabilities, count=3):
    indices = np.argsort(probabilities)[-count:][::-1]
    return [
        {
            "disease": CLASS_NAMES[int(index)],
            "confidence": round(float(probabilities[index] * 100), 2),
        }
        for index in indices
    ]


def predict_disease(image_path):
    leaf, leaf_confidence = is_leaf(image_path)
    if not leaf:
        return {
            "success": False,
            "message": "Please upload a clear image of a plant leaf.",
            "leaf_confidence": round(leaf_confidence, 2),
        }

    image = tf.keras.preprocessing.image.load_img(image_path, target_size=IMAGE_SIZE)
    image_batch = np.expand_dims(
        tf.keras.preprocessing.image.img_to_array(image), axis=0
    )
    primary_probabilities = model.predict(image_batch, verbose=0)[0]
    probabilities, agreement = blend_predictions(image_batch, primary_probabilities)

    predicted_index = int(np.argmax(probabilities))
    confidence = float(probabilities[predicted_index] * 100)
    disease = CLASS_NAMES[predicted_index]
    photo_quality = analyse_photo_quality(image_path)
    trust_score = field_trust_score(confidence, photo_quality["score"], agreement)

    log_event(
        "DISEASE DETECTED",
        {
            "disease": disease,
            "confidence": round(confidence, 2),
            "field_trust_score": trust_score,
            "ensemble_enabled": agreement is not None,
        },
    )

    return {
        "success": True,
        "disease": disease,
        "confidence": round(confidence, 2),
        "top_predictions": _top_predictions(probabilities),
        "photo_quality": photo_quality,
        "model_agreement": agreement,
        "field_trust_score": trust_score,
    }
