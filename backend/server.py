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
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

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
    Endpoint to analyze food freshness and nutrition.
    
    TODO: Replace mock prediction logic with your actual CNN model inference
    Your MobileNet + EfficientNet ensemble should:
    1. Load the uploaded image
    2. Preprocess the image
    3. Run inference to detect food type
    4. Classify freshness level
    5. Return the predictions
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
        # TODO: REPLACE THIS SECTION WITH YOUR CNN MODEL INFERENCE
        # ============================================================
        # Example integration with your model:
        # 
        # from your_model import load_model, preprocess_image, predict
        # 
        # model = load_model('path/to/your/model.h5')
        # preprocessed = preprocess_image(image)
        # food_name, freshness, confidence = model.predict(preprocessed)
        # 
        # For now, using mock predictions:
        
        # Randomly select a food item (your model will detect this)
        food_name = random.choice(list(MOCK_FOODS.keys()))
        food_data = MOCK_FOODS[food_name]
        
        # Randomly assign freshness class (your model will classify this)
        freshness_classes = ["Fresh", "Semi-Rotten", "Rotten"]
        freshness_weights = [0.6, 0.3, 0.1]  # Bias towards fresh for demo
        freshness_class = random.choices(freshness_classes, weights=freshness_weights)[0]
        
        # Mock confidence score (your model will provide this)
        confidence = random.uniform(0.85, 0.98)
        
        # ============================================================
        # END OF MOCK SECTION
        # ============================================================
        
        response = PredictionResponse(
            food_name=food_name.capitalize(),
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
