# CNN Model Integration Guide

## Overview
This guide explains how to integrate your trained CNN ensemble model (MobileNet + EfficientNet) into the Food Freshness Analysis backend API.

## Current Implementation
The backend currently uses **mock predictions** that randomly select from 5 food types (apple, banana, tomato, carrot, orange) and assign random freshness classifications. This allows the mobile app to be fully functional while you integrate your actual model.

## Integration Steps

### 1. Prepare Your Model Files
Place your trained model files in the backend directory:
```
/app/backend/
├── server.py
├── requirements.txt
├── models/
│   ├── mobilenet_efficientnet_ensemble.h5  # Your trained model
│   └── food_classes.json                    # List of food classes
```

### 2. Install Required Dependencies
Add these packages to `/app/backend/requirements.txt` if not already present:
```bash
tensorflow>=2.13.0
# or
torch>=2.0.0
torchvision>=0.15.0

opencv-python>=4.8.0
scikit-learn>=1.3.0
```

Then install:
```bash
cd /app/backend
pip install -r requirements.txt
pip freeze > requirements.txt
```

### 3. Update server.py

#### Step 3.1: Add Model Loading
At the top of `/app/backend/server.py`, add your model imports and loading:

```python
# Add these imports
import tensorflow as tf  # or import torch
import numpy as np
import cv2
import json

# Load your model at startup
MODEL_PATH = Path(__file__).parent / 'models' / 'mobilenet_efficientnet_ensemble.h5'
CLASSES_PATH = Path(__file__).parent / 'models' / 'food_classes.json'

# Load model
model = tf.keras.models.load_model(MODEL_PATH)
# or for PyTorch:
# model = torch.load(MODEL_PATH)
# model.eval()

# Load food classes and their nutritional data
with open(CLASSES_PATH, 'r') as f:
    FOOD_DATABASE = json.load(f)
```

#### Step 3.2: Replace Mock Prediction Function
Find this section in `server.py` (around line 120-135):

```python
# ============================================================
# TODO: REPLACE THIS SECTION WITH YOUR CNN MODEL INFERENCE
# ============================================================
```

Replace the entire mock section with your actual model inference:

```python
# ============================================================
# ACTUAL CNN MODEL INFERENCE
# ============================================================

def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Preprocess image for your CNN model.
    Adjust based on your model's input requirements.
    """
    # Example preprocessing for MobileNet/EfficientNet
    img_array = np.array(image.convert('RGB'))
    img_array = cv2.resize(img_array, (224, 224))  # Adjust size for your model
    img_array = img_array / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_food_and_freshness(image: Image.Image) -> tuple:
    """
    Run inference with your CNN ensemble model.
    Returns: (food_name, freshness_class, confidence)
    """
    # Preprocess
    processed_image = preprocess_image(image)
    
    # Run inference
    predictions = model.predict(processed_image)
    
    # Parse predictions based on your model output
    # Example for multi-output model:
    # food_predictions = predictions[0]  # First output: food classification
    # freshness_predictions = predictions[1]  # Second output: freshness classification
    
    # Example for single output with combined classes:
    class_idx = np.argmax(predictions[0])
    confidence = float(np.max(predictions[0]))
    
    # Map to food name and freshness
    # Adjust based on your class structure
    predicted_class = list(FOOD_DATABASE.keys())[class_idx]
    
    # If your model outputs freshness separately:
    freshness_idx = np.argmax(freshness_predictions[0])
    freshness_classes = ["Fresh", "Semi-Rotten", "Rotten"]
    freshness_class = freshness_classes[freshness_idx]
    
    return predicted_class, freshness_class, confidence

# Use the function in the endpoint
try:
    image = Image.open(BytesIO(contents))
    image.verify()
    image = Image.open(BytesIO(contents))
except Exception as e:
    raise HTTPException(status_code=400, detail="Invalid image file")

# Convert image to base64 for response
buffered = BytesIO()
image_rgb = image.convert('RGB')
image_rgb.thumbnail((800, 800))
image_rgb.save(buffered, format="JPEG")
image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

# Run your model
food_name, freshness_class, confidence = predict_food_and_freshness(image)

# Get nutritional data from your database
if food_name.lower() not in FOOD_DATABASE:
    raise HTTPException(status_code=404, detail="Food not recognized")

food_data = FOOD_DATABASE[food_name.lower()]

# ============================================================
# END OF ACTUAL MODEL INFERENCE
# ============================================================
```

### 4. Create Food Classes Database
Create `/app/backend/models/food_classes.json`:

```json
{
  "apple": {
    "nutrition": {
      "calories": 52,
      "carbs": 14,
      "protein": 0.3,
      "fat": 0.2,
      "fiber": 2.4
    },
    "bioactive_compounds": ["Quercetin", "Catechin", "Chlorogenic acid", "Anthocyanins"],
    "health_benefits": "Rich in antioxidants and fiber. Supports heart health, aids digestion, and may reduce risk of diabetes. High in vitamin C for immune support."
  },
  "banana": {
    "nutrition": {
      "calories": 89,
      "carbs": 23,
      "protein": 1.1,
      "fat": 0.3,
      "fiber": 2.6
    },
    "bioactive_compounds": ["Dopamine", "Catechin", "Resistant starch", "Pectin"],
    "health_benefits": "Excellent source of potassium for heart health. Provides quick energy, supports digestive health, and helps regulate blood sugar levels."
  }
  // ... add all your food classes
}
```

### 5. Test Your Integration

#### Test with curl:
```bash
# Create a test image
curl -X POST http://localhost:8001/api/predict \
  -F "file=@/path/to/your/test/apple.jpg" \
  | jq
```

#### Expected Response:
```json
{
  "food_name": "Apple",
  "freshness_class": "Fresh",
  "confidence": 0.94,
  "nutrition": {
    "calories": 52.0,
    "carbs": 14.0,
    "protein": 0.3,
    "fat": 0.2,
    "fiber": 2.4
  },
  "bioactive_compounds": ["Quercetin", "Catechin", "Chlorogenic acid", "Anthocyanins"],
  "health_benefits": "Rich in antioxidants and fiber...",
  "image_base64": "..."
}
```

### 6. Restart Backend
```bash
sudo supervisorctl restart backend
```

## Model Input/Output Specifications

### Expected Model Input:
- **Format**: RGB image
- **Size**: 224x224 pixels (adjust based on your model)
- **Normalization**: 0-1 range (divide by 255)
- **Batch dimension**: (1, 224, 224, 3)

### Expected Model Output:
Choose one of these architectures:

#### Option A: Multi-Output Model (Recommended)
```python
# Output 1: Food classification
food_output = model.predict(image)[0]  # Shape: (1, num_food_classes)

# Output 2: Freshness classification
freshness_output = model.predict(image)[1]  # Shape: (1, 3) for Fresh/Semi-Rotten/Rotten
```

#### Option B: Single Output with Combined Classes
```python
# Combined classes: "apple_fresh", "apple_semi_rotten", "apple_rotten", etc.
output = model.predict(image)  # Shape: (1, num_food_classes * 3)
```

## Error Handling

Add specific error handling for your model:

```python
try:
    food_name, freshness_class, confidence = predict_food_and_freshness(image)
except ValueError as e:
    raise HTTPException(status_code=400, detail=f"Invalid image for model: {str(e)}")
except Exception as e:
    logger.error(f"Model inference error: {str(e)}")
    raise HTTPException(status_code=500, detail="Model inference failed")
```

## Performance Optimization Tips

1. **Model Loading**: Load model once at startup (already done in the template)
2. **Batch Processing**: If needed, implement batch processing for multiple images
3. **Model Quantization**: Use TensorFlow Lite or ONNX for faster inference
4. **GPU Support**: Enable GPU if available:
   ```python
   # TensorFlow
   gpus = tf.config.list_physical_devices('GPU')
   if gpus:
       tf.config.experimental.set_memory_growth(gpus[0], True)
   ```

## Testing Checklist

After integration, verify:
- ✅ Model loads successfully at startup
- ✅ Predictions work for all supported food types
- ✅ Freshness classification is accurate
- ✅ Response time is acceptable (< 2 seconds)
- ✅ Error handling works for unsupported foods
- ✅ Mobile app receives and displays results correctly

## Troubleshooting

### Model Loading Errors
- Check model file path
- Verify TensorFlow/PyTorch version compatibility
- Check model file integrity

### Slow Predictions
- Consider model quantization
- Reduce image size during preprocessing
- Enable GPU acceleration

### Memory Issues
- Use model quantization
- Implement request queuing
- Add memory limits in Docker

## Support

If you encounter issues during integration:
1. Check backend logs: `tail -f /var/log/supervisor/backend.err.log`
2. Test with simple curl commands first
3. Verify model outputs match expected format
4. Check that food_classes.json includes all your model's classes

## Mobile App Integration

The mobile app is already configured to work with your model:
- Sends images as multipart/form-data
- Expects JSON response with the structure shown above
- Displays all returned data: food name, freshness, nutrition, bioactive compounds, health benefits
- No changes needed to mobile app code!

Your CNN model integration is now complete! The mobile app will automatically work with your real model predictions.
