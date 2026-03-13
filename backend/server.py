from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import logging
from pathlib import Path
from pydantic import BaseModel
import base64
from PIL import Image
from io import BytesIO
import numpy as np
import cv2
import tensorflow as tf

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# --------------------------------------------------
# Load TensorFlow model
# --------------------------------------------------
MODEL_PATH = ROOT_DIR / "models" / "food_freshness_model.h5"
model = None

try:
    try:
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    except Exception:
        model = tf.keras.models.load_model(MODEL_PATH, compile=False, safe_mode=False)

    if model:
        model.compile(
            optimizer="adam",
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )
        logging.info(f"Model loaded successfully from {MODEL_PATH}")

except Exception as e:
    logging.error(f"Model failed to load: {e}")
    model = None


# --------------------------------------------------
# FastAPI App
# --------------------------------------------------
app = FastAPI()
api_router = APIRouter(prefix="/api")


# --------------------------------------------------
# Response Models
# --------------------------------------------------
class NutritionInfo(BaseModel):
    calories: float
    carbs: float
    protein: float
    fat: float
    fiber: float


class PredictionResponse(BaseModel):
    food_name: str
    freshness_class: str
    confidence: float
    nutrition: NutritionInfo
    bioactive_compounds: list[str]
    health_benefits: str
    image_base64: str


# --------------------------------------------------
# Routes
# --------------------------------------------------
@api_router.get("/")
async def root():
    return {"message": "Food Freshness Analysis API", "version": "1.0"}


@api_router.post("/predict", response_model=PredictionResponse)
async def predict_food(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        try:
            image = Image.open(BytesIO(contents))
            image.verify()
            image = Image.open(BytesIO(contents))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Convert image to base64
        buffered = BytesIO()
        image_rgb = image.convert("RGB")
        image_rgb.thumbnail((800, 800))
        image_rgb.save(buffered, format="JPEG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # --------------------------------------------------
        # MODEL INFERENCE
        # --------------------------------------------------
        if model is not None:

            img_array = np.array(image.convert("RGB"))
            img_array = cv2.resize(img_array, (224, 224))
            img_array = img_array / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            predictions = model.predict(img_array, verbose=0)
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(np.max(predictions[0]))

            freshness_classes = ["Fresh", "Rotten", "Semi-Rotten"]
            freshness_class = freshness_classes[predicted_class_idx]

        else:

            logging.info("Using fallback color analysis")

            img_array = np.array(image.convert("RGB"))
            img_array = cv2.resize(img_array, (224, 224))

            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            _, s, v = cv2.split(hsv)

            avg_saturation = np.mean(s)
            avg_value = np.mean(v)

            if avg_value < 80:
                freshness_class = "Rotten"
                confidence = 0.75
            elif avg_saturation < 100:
                freshness_class = "Semi-Rotten"
                confidence = 0.7
            else:
                freshness_class = "Fresh"
                confidence = 0.85

        # --------------------------------------------------
        # Food info (temporary placeholder)
        # --------------------------------------------------
        food_name = "Food Item"

        if freshness_class == "Fresh":
            food_data = {
                "nutrition": {"calories": 52, "carbs": 14, "protein": 0.8, "fat": 0.3, "fiber": 2.5},
                "bioactive_compounds": ["Vitamins", "Antioxidants"],
                "health_benefits": "Fresh produce retains maximum nutrients.",
            }

        elif freshness_class == "Semi-Rotten":
            food_data = {
                "nutrition": {"calories": 48, "carbs": 13, "protein": 0.7, "fat": 0.3, "fiber": 2.2},
                "bioactive_compounds": ["Reduced Vitamins"],
                "health_benefits": "Semi-rotten produce has reduced nutrition.",
            }

        else:
            food_data = {
                "nutrition": {"calories": 40, "carbs": 11, "protein": 0.5, "fat": 0.2, "fiber": 1.8},
                "bioactive_compounds": ["Degraded Nutrients"],
                "health_benefits": "Rotten produce should be discarded.",
            }

        response = PredictionResponse(
            food_name=food_name,
            freshness_class=freshness_class,
            confidence=round(confidence, 2),
            nutrition=NutritionInfo(**food_data["nutrition"]),
            bioactive_compounds=food_data["bioactive_compounds"],
            health_benefits=food_data["health_benefits"],
            image_base64=image_base64,
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# --------------------------------------------------
# App Setup
# --------------------------------------------------
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)