import requests
import base64
from PIL import Image
import io
import sys
import os

def test_local_server():
    """Test the local Flask server"""
    print("Testing Flask Image Blender Server...")
    
    # Test server health
    try:
        response = requests.get('http://localhost:5000/')
        if response.status_code == 200:
            print("✓ Server is running")
        else:
            print("✗ Server returned status:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running. Please start the server first.")
        return False
    
    return True

def create_test_image(color, size=(200, 200), filename=None):
    """Create a test image for testing"""
    img = Image.new('RGB', size, color=color)
    if filename:
        img.save(filename)
        print(f"✓ Created test image: {filename}")
    
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    return img_io

def test_api_blend():
    """Test the blending API"""
    print("\nTesting API blending...")
    
    # Create test images
    red_image = create_test_image('red')
    blue_image = create_test_image('blue')
    
    # Prepare request
    files = {
        'image1': ('red.jpg', red_image, 'image/jpeg'),
        'image2': ('blue.jpg', blue_image, 'image/jpeg')
    }
    
    data = {
        'blend_level': '0.5'
    }
    
    try:
        response = requests.post('http://localhost:5000/api/blend', files=files, data=data)
        result = response.json()
        
        if result['success']:
            print("✓ API blending test passed")
            
            # Save result
            image_data = base64.b64decode(result['blended_image'])
            image = Image.open(io.BytesIO(image_data))
            image.save('test_blend_result.png')
            print("✓ Result saved as 'test_blend_result.png'")
            
            return True
        else:
            print("✗ API blending failed:", result.get('error', 'Unknown error'))
            return False
            
    except Exception as e:
        print("✗ API test failed:", e)
        return False

def test_advanced_processing():
    """Test advanced processing with CAPTCHA"""
    print("\nTesting advanced processing...")
    
    # First, get a new CAPTCHA
    try:
        response = requests.get('http://localhost:5000/new-captcha')
        captcha_data = response.json()
        print("✓ CAPTCHA generated")
        
        # In a real test, you'd need to solve the CAPTCHA
        # For testing, we'll use a mock session
        print("⚠ Note: CAPTCHA verification requires manual testing")
        
    except Exception as e:
        print("✗ CAPTCHA test failed:", e)
        return False
    
    return True

def main():
    """Main test function"""
    print("Flask Image Blender Client Test")
    print("=" * 40)
    
    # Test server connection
    if not test_local_server():
        return
    
    # Test API blending
    api_success = test_api_blend()
    
    # Test advanced features
    advanced_success = test_advanced_processing()
    
    print("\n" + "=" * 40)
    print("Test Summary:")
    print(f"API Blending: {'✓ PASS' if api_success else '✗ FAIL'}")
    print(f"Advanced Features: {'✓ PARTIAL' if advanced_success else '✗ FAIL'}")
    print("\nTo test CAPTCHA functionality, please use the web interface.")
    print("Open http://localhost:5000/advanced in your browser.")

if __name__ == '__main__':
    main()
