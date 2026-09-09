from pathlib import Path

import numpy as np
import tensorflow as tf

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = BASE_DIR / "models" / "leaf_validator.keras"

leaf_model = tf.keras.models.load_model(MODEL_PATH)

IMG_SIZE = (224, 224)


def is_leaf(image_path):

    img = tf.keras.preprocessing.image.load_img(
        image_path,
        target_size=IMG_SIZE
    )

    img = tf.keras.preprocessing.image.img_to_array(img)

    # Normalize exactly like training
    img = img / 255.0

    img = np.expand_dims(img, axis=0)

    prediction = float(leaf_model.predict(img, verbose=0)[0][0])

    not_leaf_prob = prediction
    leaf_prob = 1.0 - prediction

    print("\n========== Leaf Validator ==========")
    print(f"Leaf Probability     : {leaf_prob*100:.2f}%")
    print(f"Not Leaf Probability : {not_leaf_prob*100:.2f}%")
    print("====================================\n")

    # Require HIGH confidence
    if leaf_prob >= 0.75:
        return True, leaf_prob * 100

    return False, not_leaf_prob * 100