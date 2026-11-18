"""Fine-tune an ImageNet-pretrained DenseNet121 for the plant disease classes."""

import json
from pathlib import Path

import tensorflow as tf


BASE_DIR = Path(__file__).resolve().parents[2]
TRAIN_DIR = BASE_DIR / "ai" / "dataset" / "train"
CLASS_NAMES_PATH = BASE_DIR / "ai" / "models" / "class_names.json"
OUTPUT_PATH = BASE_DIR / "ai" / "models" / "densenet121_plant_disease.keras"
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32


def main():
    with CLASS_NAMES_PATH.open("r", encoding="utf-8") as file:
        expected_classes = json.load(file)

    train_data = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        labels="inferred",
        label_mode="categorical",
        class_names=expected_classes,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        validation_split=0.2,
        subset="training",
        seed=42,
    )
    validation_data = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        labels="inferred",
        label_mode="categorical",
        class_names=expected_classes,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        validation_split=0.2,
        subset="validation",
        seed=42,
    )
    autotune = tf.data.AUTOTUNE
    train_data = train_data.prefetch(autotune)
    validation_data = validation_data.prefetch(autotune)

    augmentation = tf.keras.Sequential(
        [
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomRotation(0.08),
            tf.keras.layers.RandomZoom(0.1),
        ],
        name="augmentation",
    )
    backbone = tf.keras.applications.DenseNet121(
        include_top=False,
        weights="imagenet",
        input_shape=(*IMAGE_SIZE, 3),
    )
    backbone.trainable = False
    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3))
    x = augmentation(inputs)
    x = tf.keras.applications.densenet.preprocess_input(x)
    x = backbone(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(len(expected_classes), activation="softmax")(x)
    model = tf.keras.Model(inputs, outputs, name="densenet121_plant_disease")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=4, restore_best_weights=True
        ),
        tf.keras.callbacks.ModelCheckpoint(
            OUTPUT_PATH, monitor="val_accuracy", save_best_only=True
        ),
    ]
    model.fit(
        train_data,
        validation_data=validation_data,
        epochs=15,
        callbacks=callbacks,
    )

    backbone.trainable = True
    for layer in backbone.layers[:-40]:
        layer.trainable = False
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(
        train_data,
        validation_data=validation_data,
        epochs=8,
        callbacks=callbacks,
    )
    model.save(OUTPUT_PATH)
    print(f"Saved DenseNet121 model to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
