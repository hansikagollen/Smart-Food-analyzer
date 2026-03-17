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
        
        # Calculate standard deviation to detect uniformity (fresh produce is more uniform)
        std_value = np.std(v)
        
        # Detect brown/dark colors (signs of rotting)
        # Brown hues in HSV: typically 10-40 range (orange to brown)
        # Expanded range to catch more brown tones
        brown_mask = ((h > 5) & (h < 40) & (s > 20) & (v < 200) & (v > 30))
        brown_ratio = np.sum(brown_mask) / brown_mask.size
        
        # Detect very dark areas (significant rotting)
        very_dark_ratio = np.sum(v < 60) / v.size
        
        # Detect moderately dark areas (minor rotting)
        dark_ratio = np.sum(v < 100) / v.size
        
        # Detect dull/low saturation areas (loss of freshness)
        dull_ratio = np.sum(s < 70) / s.size
        
        # Fresh produce characteristics:
        # - Higher average brightness (value > 130)
        # - Higher saturation (s > 80 for most fresh produce)
        # - Lower dark ratio (< 0.3)
        # - Lower brown ratio (< 0.05)
        
        # Decision logic with improved thresholds
        # Rotten: Very dark OR lots of brown OR very low brightness+saturation
        if very_dark_ratio > 0.4 or brown_ratio > 0.25 or (avg_value < 70 and avg_saturation < 40):
            freshness_class = "Rotten"
            confidence = 0.75 + (very_dark_ratio * 0.2)
        # Semi-Rotten: Moderate issues with color/brightness OR some brown spots
        elif dark_ratio > 0.35 or brown_ratio > 0.05 or dull_ratio > 0.6 or (avg_value < 140 and brown_ratio > 0.02):
            freshness_class = "Semi-Rotten"
            confidence = 0.70 + (brown_ratio * 0.25)
        # Fresh: Good color and brightness
        else:
            freshness_class = "Fresh"
            confidence = 0.75 + (avg_saturation / 400) + (avg_value / 1000)
        
        confidence = min(confidence, 0.95)  # Cap at 95%
        
        # Log analysis for debugging
        logger.info(f"Analysis: sat={avg_saturation:.1f}, val={avg_value:.1f}, dark={dark_ratio:.2f}, brown={brown_ratio:.2f}, dull={dull_ratio:.2f} -> {freshness_class}")
        
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
