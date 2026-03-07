import tensorflow as tf
import numpy as np
import cv2
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent / "models" / "food_freshness_model.h5"

model = tf.keras.models.load_model(MODEL_PATH)

classes = ["Fresh","Semi-Rotten","Rotten"]

def predict_freshness(image):

    img = np.array(image.convert("RGB"))
    img = cv2.resize(img,(224,224))

    img = img/255.0
    img = np.expand_dims(img,axis=0)

    prediction = model.predict(img)

    index = np.argmax(prediction)
    confidence = float(np.max(prediction))

    freshness = classes[index]

    return freshness, confidence