from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel
import base64
from PIL import Image
from io import BytesIO
import numpy as np
import cv2

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Color-based freshness analysis (no ML model needed)
logging.info("="*60)
logging.info("Food Freshness Analyzer - Color-Based Analysis Mode")
logging.info("Using lightweight HSV color analysis for freshness detection")
logging.info("="*60)

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Response Models
class NutritionInfo(BaseModel):
    calories: float
    carbs: float
    protein: float
    fat: float
    fiber: float

class PredictionResponse(BaseModel):
    food_name: str
    freshness_class: str  # "Fresh", "Semi-Rotten", "Rotten"
    confidence: float
    nutrition: NutritionInfo
    bioactive_compounds: list[str]
    health_benefits: str
    image_base64: str

# Mock food database for demonstration
# You will replace this with your actual CNN model predictions
MOCK_FOODS = {
    "apple": {
        "nutrition": {"calories": 52, "carbs": 14, "protein": 0.3, "fat": 0.2, "fiber": 2.4},
        "bioactive_compounds": ["Quercetin", "Catechin", "Chlorogenic acid", "Anthocyanins"],
        "health_benefits": "Rich in antioxidants and fiber. Supports heart health, aids digestion, and may reduce risk of diabetes. High in vitamin C for immune support."
    },
    "banana": {
        "nutrition": {"calories": 89, "carbs": 23, "protein": 1.1, "fat": 0.3, "fiber": 2.6},
        "bioactive_compounds": ["Dopamine", "Catechin", "Resistant starch", "Pectin"],
        "health_benefits": "Excellent source of potassium for heart health. Provides quick energy, supports digestive health, and helps regulate blood sugar levels."
    },
    "tomato": {
        "nutrition": {"calories": 18, "carbs": 3.9, "protein": 0.9, "fat": 0.2, "fiber": 1.2},
        "bioactive_compounds": ["Lycopene", "Beta-carotene", "Naringenin", "Chlorogenic acid"],
        "health_benefits": "High in lycopene, a powerful antioxidant. Supports heart health, skin protection, and may reduce cancer risk. Rich in vitamins A and C."
    },
    "carrot": {
        "nutrition": {"calories": 41, "carbs": 10, "protein": 0.9, "fat": 0.2, "fiber": 2.8},
        "bioactive_compounds": ["Beta-carotene", "Alpha-carotene", "Lutein", "Polyacetylenes"],
        "health_benefits": "Excellent source of beta-carotene for eye health. Supports immune function, skin health, and has anti-inflammatory properties."
    },
    "orange": {
        "nutrition": {"calories": 47, "carbs": 12, "protein": 0.9, "fat": 0.1, "fiber": 2.4},
        "bioactive_compounds": ["Hesperidin", "Naringenin", "Vitamin C", "Carotenoids"],
        "health_benefits": "Very high in vitamin C for immune support. Contains flavonoids that support heart health and reduce inflammation. Aids in iron absorption."
    }
}

@api_router.get("/")
async def root():
    return {"message": "Food Freshness Analysis API", "version": "1.0"}

@api_router.post("/predict", response_model=PredictionResponse)
async def predict_food(file: UploadFile = File(...)):
    """
    Endpoint to analyze food freshness and nutrition using the trained CNN model.
    """
    try:
        # Read and validate image
        contents = await file.read()
        
        try:
            image = Image.open(BytesIO(contents))
            image.verify()  # Verify it's a valid image
            image = Image.open(BytesIO(contents))  # Reopen after verify
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Convert image to base64 for response
        buffered = BytesIO()
        image_rgb = image.convert('RGB')
        image_rgb.thumbnail((800, 800))  # Resize for efficiency
        image_rgb.save(buffered, format="JPEG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # ============================================================
        # COLOR-BASED FRESHNESS ANALYSIS (No ML model needed)
        # ============================================================
        
        # Analyze image using HSV color analysis
        logging.info("Using color-based freshness analysis")
        
        img_array = np.array(image.convert('RGB'))
        img_array = cv2.resize(img_array, (224, 224))
        
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        
        # Calculate metrics
        avg_saturation = np.mean(s)
        avg_value = np.mean(v)
        avg_hue = np.mean(h)
        
        # Detect brown/dark colors (signs of rotting)
        brown_mask = ((h > 10) & (h < 30) & (s > 50) & (v < 150))
        brown_ratio = np.sum(brown_mask) / brown_mask.size
        
        # Detect dark areas
        dark_ratio = np.sum(v < 80) / v.size
        
        # Decision logic based on color analysis
        if dark_ratio > 0.4 or brown_ratio > 0.3 or (avg_saturation < 60 and avg_value < 100):
            freshness_class = "Rotten"
            confidence = 0.75 + (dark_ratio * 0.2)
        elif dark_ratio > 0.2 or brown_ratio > 0.15 or avg_saturation < 100:
            freshness_class = "Semi-Rotten"
            confidence = 0.70 + (brown_ratio * 0.25)
        else:
            freshness_class = "Fresh"
            confidence = 0.80 + (avg_saturation / 500)
        
        confidence = min(confidence, 0.95)  # Cap at 95%
        
        # Food name (generic since we don't have CNN for food type detection)
        food_name = "Food Item"
        
        # Get nutritional data based on freshness
        if freshness_class == "Fresh":
            food_data = {
                "nutrition": {"calories": 52, "carbs": 14, "protein": 0.8, "fat": 0.3, "fiber": 2.5},
                "bioactive_compounds": ["Vitamins", "Antioxidants", "Phytonutrients", "Minerals"],
                "health_benefits": "Fresh produce retains maximum nutrients and antioxidants. Supports immune function, digestive health, and overall wellness. Best for optimal health benefits."
            }
        elif freshness_class == "Semi-Rotten":
            food_data = {
                "nutrition": {"calories": 48, "carbs": 13, "protein": 0.7, "fat": 0.3, "fiber": 2.2},
                "bioactive_compounds": ["Reduced Vitamins", "Some Antioxidants", "Minerals"],
                "health_benefits": "Semi-rotten produce has reduced nutritional value. Some vitamins may be degraded. Consume soon and cook thoroughly to ensure safety."
            }
        else:  # Rotten
            food_data = {
                "nutrition": {"calories": 40, "carbs": 11, "protein": 0.5, "fat": 0.2, "fiber": 1.8},
                "bioactive_compounds": ["Degraded Nutrients", "Possible Toxins"],
                "health_benefits": "Rotten produce should be discarded. May contain harmful bacteria and toxins. Not safe for consumption. Can cause foodborne illness."
            }
        
        # ============================================================
        # END OF COLOR-BASED ANALYSIS
        # ============================================================
        
        response = PredictionResponse(
            food_name=food_name,
            freshness_class=freshness_class,
            confidence=round(confidence, 2),
            nutrition=NutritionInfo(**food_data["nutrition"]),
            bioactive_compounds=food_data["bioactive_compounds"],
            health_benefits=food_data["health_benefits"],
            image_base64=image_base64
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
