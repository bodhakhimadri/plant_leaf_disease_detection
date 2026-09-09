import json
from pathlib import Path

import numpy as np
import tensorflow as tf

from backend.src.logger import log_event

from ai.leaf_validation.leaf_predict import is_leaf

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "ai" / "models" / "trained_plant_disease_model.keras"
CLASS_NAMES_PATH = BASE_DIR / "ai" / "models" / "class_names.json"

# -----------------------------
# Load model only once
# -----------------------------
model = tf.keras.models.load_model(
    MODEL_PATH,
    compile=False
)

# -----------------------------
# Load class names
# -----------------------------
with open(CLASS_NAMES_PATH, "r") as f:
    CLASS_NAMES = json.load(f)

print("Model loaded from:", MODEL_PATH)
print("Input shape:", model.input_shape)
print("Number of classes:", len(CLASS_NAMES))


# -----------------------------
# Prediction Function
# -----------------------------
def predict_disease(image_path):

    leaf, leaf_confidence = is_leaf(image_path)

    if not leaf:
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

    prediction = model.predict(img_array, verbose=0)[0]

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

    return {
    "success": True,
    "disease": disease,
    "confidence": confidence
    }