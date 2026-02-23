# Smart Food Quality Analyzer

An AI-powered mobile application for food freshness and nutrition analysis using computer vision.

## Overview

This cross-platform mobile app (iOS & Android) allows users to:
- 📸 Capture or upload images of fruits/vegetables
- 🤖 Analyze food freshness using AI (Fresh/Semi-Rotten/Rotten)
- 🥗 Get detailed nutritional information (calories, carbs, protein, fat, fiber)
- 💊 View bioactive compounds and health benefits
- 📊 Store and view analysis history locally (offline capability)

## Features

### Mobile App Screens
1. **Splash Screen** - Beautiful branded introduction
2. **Home Screen** - Three main actions: Capture, Upload, or View History
3. **Loading Screen** - Real-time analysis progress with animations
4. **Result Screen** - Comprehensive display of food analysis with color-coded freshness badges
5. **History Screen** - Local storage of all past analyses (works offline)

### Backend API
- **POST /api/predict** - Accepts image uploads, returns food analysis
- Mock predictions ready to be replaced with your CNN model
- Supports: food classification, freshness detection, nutrition data, bioactive compounds

## Architecture

```
├── frontend/                  # Expo React Native mobile app
│   ├── app/                  # Screens (Expo Router)
│   │   ├── index.tsx        # Splash screen
│   │   ├── home.tsx         # Main menu
│   │   ├── loading.tsx      # Analysis screen
│   │   ├── result.tsx       # Results display
│   │   └── history.tsx      # History view
│   ├── app.json             # Expo configuration
│   └── package.json         # Dependencies
├── backend/                  # FastAPI Python backend
│   ├── server.py            # API endpoints
│   └── requirements.txt     # Python packages
└── CNN_MODEL_INTEGRATION_GUIDE.md  # Model integration instructions
```

## Technology Stack

### Frontend
- **Expo** (v54) - Cross-platform mobile development
- **React Native** (v0.81) - Native UI components
- **Expo Router** - File-based navigation
- **Expo Image Picker** - Camera & gallery access
- **AsyncStorage** - Local data persistence
- **Axios** - API communication

### Backend
- **FastAPI** - Modern Python web framework
- **Pillow** - Image processing
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## Getting Started

### Prerequisites
- Node.js 18+ and Yarn
- Python 3.11+
- Expo Go app (for mobile testing)

### Installation

1. **Clone and Navigate**
   ```bash
   cd /app
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd frontend
   yarn install
   ```

3. **Install Backend Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### Running the App

1. **Start Backend Server**
   ```bash
   sudo supervisorctl restart backend
   # Backend runs at http://localhost:8001
   ```

2. **Start Frontend**
   ```bash
   sudo supervisorctl restart expo
   # Frontend runs at http://localhost:3000
   ```

3. **Access the App**
   - **Web Preview**: https://nutrition-ai-check.preview.emergentagent.com
   - **Mobile (Expo Go)**: Scan QR code from terminal
   - **iOS/Android**: Build with `eas build`

## API Documentation

### GET /api/
Health check endpoint
```json
{
  "message": "Food Freshness Analysis API",
  "version": "1.0"
}
```

### POST /api/predict
Analyze food image

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image file - JPEG/PNG)

**Response:**
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
  "bioactive_compounds": [
    "Quercetin",
    "Catechin",
    "Chlorogenic acid",
    "Anthocyanins"
  ],
  "health_benefits": "Rich in antioxidants and fiber...",
  "image_base64": "..."
}
```

## Integrating Your CNN Model

The backend currently uses **mock predictions** for demonstration. To integrate your trained MobileNet + EfficientNet ensemble model:

**📖 See detailed instructions in:** [`CNN_MODEL_INTEGRATION_GUIDE.md`](./CNN_MODEL_INTEGRATION_GUIDE.md)

Quick steps:
1. Place model file in `/app/backend/models/`
2. Update `server.py` with your model loading code
3. Replace mock prediction logic with your inference code
4. Restart backend: `sudo supervisorctl restart backend`

The mobile app requires **no changes** - it's already configured to work with your real model!

## Testing

### Backend Testing
```bash
# Test health endpoint
curl http://localhost:8001/api/

# Test prediction endpoint
curl -X POST http://localhost:8001/api/predict \
  -F "file=@/path/to/image.jpg" | jq
```

### Frontend Testing
- **Web**: Open browser at https://nutrition-ai-check.preview.emergentagent.com
- **Mobile**: Use Expo Go app to scan QR code
- **Automated**: Testing completed - see `test_result.md`

## Project Status

✅ **MVP Complete** - All core features implemented and tested

### Backend
- ✅ Image upload endpoint with validation
- ✅ Mock predictions (5 food types: apple, banana, tomato, carrot, orange)
- ✅ Comprehensive error handling
- ✅ Base64 image encoding for mobile
- ✅ CORS configured for cross-platform access
- ✅ Performance optimized (< 1 second response time)
- ✅ All 12 test scenarios passing

### Frontend
- ✅ Beautiful Material Design UI
- ✅ Splash screen with branding
- ✅ Camera capture functionality
- ✅ Gallery image selection
- ✅ Real-time analysis with loading animation
- ✅ Color-coded freshness display (Green/Yellow/Red)
- ✅ Nutrition table with icons
- ✅ Bioactive compounds display
- ✅ Health benefits explanation
- ✅ Local history storage (AsyncStorage)
- ✅ Offline history viewing
- ✅ Delete and clear history options
- ✅ Proper permission handling (camera & gallery)
- ✅ Cross-platform compatibility (iOS/Android/Web)

## Permissions

### iOS (app.json)
- `NSCameraUsageDescription`: "Capture food photos for freshness analysis"
- `NSPhotoLibraryUsageDescription`: "Select food photos for analysis"

### Android (app.json)
- `CAMERA`
- `READ_EXTERNAL_STORAGE`
- `WRITE_EXTERNAL_STORAGE`
- `READ_MEDIA_IMAGES`

## UI/UX Features

- **Dark Theme** with teal accent (#4ecca3)
- **Color-Coded Freshness Badges**:
  - 🟢 Green = Fresh
  - 🟡 Yellow = Semi-Rotten
  - 🔴 Red = Rotten
- **Nutrition Icons** for calories, carbs, protein, fat, fiber
- **Smooth Animations** for loading states
- **Responsive Layout** for all screen sizes
- **Touch-Optimized** buttons and controls

## Troubleshooting

### Backend Issues
```bash
# Check backend logs
tail -f /var/log/supervisor/backend.err.log

# Restart backend
sudo supervisorctl restart backend
```

### Frontend Issues
```bash
# Check expo logs
tail -f /var/log/supervisor/expo.err.log

# Restart frontend
sudo supervisorctl restart expo

# Clear cache
cd frontend && yarn start --clear
```

### Common Issues
1. **"Food not recognized"** - Backend returning error or mock data
2. **Permissions denied** - Check app.json permissions configuration
3. **Image not uploading** - Check network connectivity and CORS settings

## Future Enhancements

Potential improvements:
- 🔄 Add more food types to database
- 📈 Add nutritional goal tracking
- 🌐 Multi-language support
- 📸 Batch image analysis
- 🔔 Freshness expiration reminders
- ☁️ Optional cloud sync for history
- 📊 Nutritional statistics and charts
- 🤝 Social sharing of results

## License

This project is ready for your CNN model integration and deployment!

## Support

- Backend API: http://localhost:8001/docs (FastAPI auto-docs)
- Check `test_result.md` for detailed test results
- See `CNN_MODEL_INTEGRATION_GUIDE.md` for model integration help

---

**Built with ❤️ using Expo, React Native, and FastAPI**
