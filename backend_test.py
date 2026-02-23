#!/usr/bin/env python3
"""
Backend API Tests for Food Freshness Analysis System
Tests the /api/ and /api/predict endpoints with various scenarios
"""

import requests
import base64
import json
import time
from PIL import Image
from io import BytesIO
import os
import sys

# Backend URL from frontend environment
BACKEND_URL = "https://nutrition-ai-check.preview.emergentagent.com/api"

def create_test_image(size=(400, 400), format='JPEG', color='RGB'):
    """Create a test image of specified size and format"""
    image = Image.new(color, size, color='red')
    buffer = BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return buffer

def create_large_test_image():
    """Create a large test image (2000x2000)"""
    return create_test_image(size=(2000, 2000))

def create_small_test_image():
    """Create a small test image (100x100)"""
    return create_test_image(size=(100, 100))

def create_corrupted_image():
    """Create corrupted image data"""
    return BytesIO(b"corrupted image data")

def test_health_check():
    """Test GET /api/ endpoint"""
    print("\n=== Testing Health Check Endpoint ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "Food Freshness Analysis API" and data.get("version") == "1.0":
                print("✅ Health check passed")
                return True
            else:
                print("❌ Health check failed - incorrect response format")
                return False
        else:
            print(f"❌ Health check failed - status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed with error: {e}")
        return False

def test_predict_valid_jpeg():
    """Test POST /api/predict with valid JPEG image"""
    print("\n=== Testing Valid JPEG Image ===")
    
    try:
        test_image = create_test_image(format='JPEG')
        files = {'file': ('test.jpg', test_image, 'image/jpeg')}
        
        start_time = time.time()
        response = requests.post(f"{BACKEND_URL}/predict", files=files)
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            
            # Validate response structure
            required_fields = ['food_name', 'freshness_class', 'confidence', 'nutrition', 'bioactive_compounds', 'health_benefits', 'image_base64']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Validate field types and values
            if not isinstance(data['food_name'], str):
                print("❌ food_name is not a string")
                return False
                
            if data['freshness_class'] not in ['Fresh', 'Semi-Rotten', 'Rotten']:
                print(f"❌ Invalid freshness_class: {data['freshness_class']}")
                return False
                
            if not isinstance(data['confidence'], (int, float)) or not (0 <= data['confidence'] <= 1):
                print(f"❌ Invalid confidence value: {data['confidence']}")
                return False
            
            # Validate nutrition object
            nutrition = data['nutrition']
            nutrition_fields = ['calories', 'carbs', 'protein', 'fat', 'fiber']
            for field in nutrition_fields:
                if field not in nutrition or not isinstance(nutrition[field], (int, float)):
                    print(f"❌ Invalid nutrition field: {field}")
                    return False
            
            # Validate bioactive_compounds is array
            if not isinstance(data['bioactive_compounds'], list):
                print("❌ bioactive_compounds is not an array")
                return False
            
            # Validate health_benefits is string
            if not isinstance(data['health_benefits'], str):
                print("❌ health_benefits is not a string")
                return False
            
            # Validate base64 image
            try:
                base64.b64decode(data['image_base64'])
                print("✅ Base64 image is valid")
            except Exception:
                print("❌ Invalid base64 image")
                return False
            
            print("✅ Valid JPEG test passed")
            print(f"Food: {data['food_name']}, Freshness: {data['freshness_class']}, Confidence: {data['confidence']}")
            return True
        else:
            print(f"❌ Valid JPEG test failed - status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Valid JPEG test failed with error: {e}")
        return False

def test_predict_valid_png():
    """Test POST /api/predict with valid PNG image"""
    print("\n=== Testing Valid PNG Image ===")
    
    try:
        test_image = create_test_image(format='PNG')
        files = {'file': ('test.png', test_image, 'image/png')}
        
        response = requests.post(f"{BACKEND_URL}/predict", files=files)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Valid PNG test passed")
            print(f"Food: {data['food_name']}, Freshness: {data['freshness_class']}")
            return True
        else:
            print(f"❌ Valid PNG test failed - status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Valid PNG test failed with error: {e}")
        return False

def test_predict_small_image():
    """Test POST /api/predict with small image (100x100)"""
    print("\n=== Testing Small Image (100x100) ===")
    
    try:
        test_image = create_small_test_image()
        files = {'file': ('small.jpg', test_image, 'image/jpeg')}
        
        response = requests.post(f"{BACKEND_URL}/predict", files=files)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Small image test passed")
            return True
        else:
            print(f"❌ Small image test failed - status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Small image test failed with error: {e}")
        return False

def test_predict_large_image():
    """Test POST /api/predict with large image (2000x2000)"""
    print("\n=== Testing Large Image (2000x2000) ===")
    
    try:
        test_image = create_large_test_image()
        files = {'file': ('large.jpg', test_image, 'image/jpeg')}
        
        start_time = time.time()
        response = requests.post(f"{BACKEND_URL}/predict", files=files, timeout=30)
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            if end_time - start_time < 5:
                print("✅ Large image test passed with good performance")
            else:
                print("⚠️ Large image test passed but response time > 5 seconds")
            return True
        else:
            print(f"❌ Large image test failed - status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Large image test failed with error: {e}")
        return False

def test_predict_invalid_file():
    """Test POST /api/predict with non-image file"""
    print("\n=== Testing Invalid File (Not an Image) ===")
    
    try:
        # Send text file instead of image
        text_data = BytesIO(b"This is not an image file")
        files = {'file': ('test.txt', text_data, 'text/plain')}
        
        response = requests.post(f"{BACKEND_URL}/predict", files=files)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Invalid file test passed - correctly rejected non-image")
            return True
        else:
            print(f"❌ Invalid file test failed - expected 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid file test failed with error: {e}")
        return False

def test_predict_empty_file():
    """Test POST /api/predict with empty file"""
    print("\n=== Testing Empty File ===")
    
    try:
        empty_file = BytesIO(b"")
        files = {'file': ('empty.jpg', empty_file, 'image/jpeg')}
        
        response = requests.post(f"{BACKEND_URL}/predict", files=files)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Empty file test passed - correctly rejected empty file")
            return True
        else:
            print(f"❌ Empty file test failed - expected 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Empty file test failed with error: {e}")
        return False

def test_predict_corrupted_image():
    """Test POST /api/predict with corrupted image data"""
    print("\n=== Testing Corrupted Image ===")
    
    try:
        corrupted_image = create_corrupted_image()
        files = {'file': ('corrupted.jpg', corrupted_image, 'image/jpeg')}
        
        response = requests.post(f"{BACKEND_URL}/predict", files=files)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Corrupted image test passed - correctly rejected corrupted data")
            return True
        else:
            print(f"❌ Corrupted image test failed - expected 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Corrupted image test failed with error: {e}")
        return False

def test_predict_missing_file():
    """Test POST /api/predict without file parameter"""
    print("\n=== Testing Missing File Parameter ===")
    
    try:
        response = requests.post(f"{BACKEND_URL}/predict")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 422:  # FastAPI returns 422 for validation errors
            print("✅ Missing file test passed - correctly rejected missing file")
            return True
        else:
            print(f"❌ Missing file test failed - expected 422, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Missing file test failed with error: {e}")
        return False

def test_predict_unsupported_format():
    """Test POST /api/predict with unsupported file format"""
    print("\n=== Testing Unsupported File Format (WEBP) ===")
    
    try:
        # Create a simple binary file pretending to be WEBP
        fake_webp = BytesIO(b"RIFF\x00\x00\x00\x00WEBP")
        files = {'file': ('test.webp', fake_webp, 'image/webp')}
        
        response = requests.post(f"{BACKEND_URL}/predict", files=files)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Unsupported format test passed - correctly rejected unsupported format")
            return True
        else:
            print(f"❌ Unsupported format test failed - expected 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Unsupported format test failed with error: {e}")
        return False

def run_all_tests():
    """Run all backend API tests"""
    print(f"Starting backend API tests for: {BACKEND_URL}")
    print("=" * 60)
    
    test_results = []
    
    # Test functions
    tests = [
        ("Health Check", test_health_check),
        ("Valid JPEG Image", test_predict_valid_jpeg),
        ("Valid PNG Image", test_predict_valid_png),
        ("Small Image", test_predict_small_image),
        ("Large Image", test_predict_large_image),
        ("Invalid File", test_predict_invalid_file),
        ("Empty File", test_predict_empty_file),
        ("Corrupted Image", test_predict_corrupted_image),
        ("Missing File Parameter", test_predict_missing_file),
        ("Unsupported Format", test_predict_unsupported_format)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(test_results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)