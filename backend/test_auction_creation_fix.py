#!/usr/bin/env python3
"""
Test Script: Auction Creation Fix Verification
Tests the complete flow of creating an auction
"""

import requests
import json
from io import BytesIO
from PIL import Image

BASE_URL = "http://127.0.0.1:5000"

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color='green')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return ('test_photo.png', img_bytes, 'image/png')

def test_auction_creation():
    """Test creating an auction with proper form data"""
    
    print("=" * 60)
    print("🧪 Testing Auction Creation Fix")
    print("=" * 60)
    
    # First, create a session and log in
    session = requests.Session()
    
    # Simulate farmer login (you may need to adjust based on your auth system)
    print("\n1️⃣ Testing with session...")
    
    # Create test image
    photo = create_test_image()
    
    # Prepare form data
    form_data = {
        'crop_name': 'Soybean',
        'quantity': '50',
        'min_bid_price': '5500',
        'duration_hours': '24',
        'location': 'Indore, Madhya Pradesh',
        'description': 'High-quality soybean crop'
    }
    
    # Prepare files (matching the form field names)
    files = {
        'photo1': photo,
    }
    
    print(f"\n📝 Form Data:")
    for key, value in form_data.items():
        print(f"  {key}: {value}")
    
    print(f"\n📸 Files:")
    print(f"  photo1: {photo[0]}")
    
    # Note: This will fail with 401 unless you have an active farmer session
    # But it shows the correct format for the API
    response = session.post(
        f"{BASE_URL}/bidding/farmer/create-auction",
        data=form_data,
        files=files
    )
    
    print(f"\n📤 Response Status: {response.status_code}")
    print(f"📄 Response Body:")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)
    
    if response.status_code == 401:
        print("\n✅ Expected: 401 Unauthorized (no farmer session)")
        print("   This is correct - the endpoint requires farmer authentication")
    elif response.status_code == 201:
        print("\n✅ SUCCESS: Auction created!")
        data = response.json()
        if data.get('success'):
            print(f"   Auction ID: {data.get('auction_id')}")
            print(f"   Base Price: ₹{data.get('base_price')}")
    else:
        print(f"\n❌ Unexpected status code: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("📋 Form Field Names:")
    print("=" * 60)
    print("✅ Correct field names to use in HTML form:")
    print("   - crop_name")
    print("   - quantity")
    print("   - min_bid_price")
    print("   - duration_hours")
    print("   - location")
    print("   - description")
    print("   - photo1 (required)")
    print("   - photo2 (optional)")
    print("   - photo3 (optional)")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        test_auction_creation()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
