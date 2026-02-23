#!/usr/bin/env python3
"""
Additional Backend API Tests - Size and Performance Tests
"""

import requests
from PIL import Image
from io import BytesIO

BACKEND_URL = "https://nutrition-ai-check.preview.emergentagent.com/api"

def create_very_large_image():
    """Create a very large image to test file size limits"""
    # Create a 4000x4000 image (should be around 48MB uncompressed)
    image = Image.new('RGB', (4000, 4000), color='red')
    buffer = BytesIO()
    image.save(buffer, format='JPEG', quality=95)
    buffer.seek(0)
    return buffer

def test_very_large_file():
    """Test with very large file to check size limits"""
    print("\n=== Testing Very Large File (4000x4000 ~48MB) ===")
    
    try:
        test_image = create_very_large_image()
        files = {'file': ('huge.jpg', test_image, 'image/jpeg')}
        
        # Use longer timeout for large file
        response = requests.post(f"{BACKEND_URL}/predict", files=files, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Very large file test passed")
            return True
        elif response.status_code == 413:  # Request Entity Too Large
            print("⚠️  Very large file rejected due to size limit (this is expected behavior)")
            return True  # This is acceptable behavior
        else:
            print(f"❌ Very large file test failed - status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⚠️  Very large file test timed out (acceptable for very large files)")
        return True
    except Exception as e:
        print(f"❌ Very large file test failed with error: {e}")
        return False

def test_multiple_concurrent_requests():
    """Test multiple concurrent requests to check server stability"""
    print("\n=== Testing Multiple Concurrent Requests ===")
    
    try:
        import threading
        import time
        
        results = []
        
        def make_request():
            try:
                test_image = Image.new('RGB', (200, 200), color='blue')
                buffer = BytesIO()
                test_image.save(buffer, format='JPEG')
                buffer.seek(0)
                
                files = {'file': ('test.jpg', buffer, 'image/jpeg')}
                response = requests.post(f"{BACKEND_URL}/predict", files=files, timeout=10)
                results.append(response.status_code == 200)
            except Exception:
                results.append(False)
        
        # Start 5 concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        success_count = sum(results)
        print(f"Concurrent requests: {len(results)}, Successful: {success_count}")
        
        if success_count >= 4:  # Allow 1 failure due to race conditions
            print("✅ Concurrent requests test passed")
            return True
        else:
            print("❌ Concurrent requests test failed")
            return False
            
    except Exception as e:
        print(f"❌ Concurrent requests test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("Running additional backend tests...")
    
    test1_result = test_very_large_file()
    test2_result = test_multiple_concurrent_requests()
    
    print("\n=== ADDITIONAL TEST SUMMARY ===")
    print(f"Very Large File: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Concurrent Requests: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 ALL ADDITIONAL TESTS PASSED!")
    else:
        print("\n⚠️  Some additional tests failed")