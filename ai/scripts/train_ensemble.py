"""Train the optional EfficientNetB0 member of LeafCare's hybrid ensemble."""

import json
from pathlib import Path

import tensorflow as tf

BASE_DIR = Path(__file__).resolve().parents[2]
TRAIN_DIR = BASE_DIR / "ai" / "dataset" / "train"
VALID_DIR = BASE_DIR / "ai" / "dataset" / "valid"
CLASS_PATH = BASE_DIR / "ai" / "models" / "class_names.json"
OUTPUT_PATH = BASE_DIR / "ai" / "models" / "efficientnet_disease_model.keras"
IMAGE_SIZE = (128, 128)


def main():
    train_data = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR, image_size=IMAGE_SIZE, batch_size=32, label_mode="int"
    )
    valid_data = tf.keras.utils.image_dataset_from_directory(
        VALID_DIR, image_size=IMAGE_SIZE, batch_size=32, label_mode="int"
    )
    expected_classes = json.loads(CLASS_PATH.read_text(encoding="utf-8"))
    if train_data.class_names != expected_classes:
        raise ValueError(
            "Dataset class order differs from ai/models/class_names.json. "
            "Fix the folder names before training an ensemble model."
        )

    augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.1),
        tf.keras.layers.RandomZoom(0.1),
        tf.keras.layers.RandomContrast(0.1),
    ])
    backbone = tf.keras.applications.EfficientNetB0(
        include_top=False, weights="imagenet", input_shape=(*IMAGE_SIZE, 3)
    )
    backbone.trainable = False
    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3))
    features = backbone(augmentation(inputs), training=False)
    features = tf.keras.layers.GlobalAveragePooling2D()(features)
    features = tf.keras.layers.Dropout(0.35)(features)
    outputs = tf.keras.layers.Dense(len(expected_classes), activation="softmax")(features)
    ensemble_model = tf.keras.Model(inputs, outputs)
    ensemble_model.compile(
        optimizer=tf.keras.optimizers.Adam(1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", mode="max", patience=4, restore_best_weights=True
        ),
        tf.keras.callbacks.ModelCheckpoint(
            OUTPUT_PATH, monitor="val_accuracy", mode="max", save_best_only=True
        ),
    ]
    ensemble_model.fit(
        train_data.prefetch(tf.data.AUTOTUNE),
        validation_data=valid_data.prefetch(tf.data.AUTOTUNE),
        epochs=15,
        callbacks=callbacks,
    )
    print(f"Saved optional ensemble model to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
