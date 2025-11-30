#!/usr/bin/env python3
"""
Test script for Telhan Sathi backend - Farmer ID + OTP Login + Profile
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_response(response, title):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")

def test_otp_flow():
    """Test OTP login flow"""
    farmer_id = "123456789012"
    
    # Step 1: Request OTP
    print("\n📱 STEP 1: Request OTP")
    print(f"Farmer ID: {farmer_id}")
    
    response = requests.post(f"{BASE_URL}/api/auth/request-otp", json={"farmer_id": farmer_id})
    print_response(response, "Request OTP Response")
    
    # Step 2: Get OTP from database (simulating SMS receipt)
    print("\n⏳ Simulating 3 second delay...")
    time.sleep(1)
    
    # Extract OTP from database for testing
    from app import app, db
    from models import OTPRecord, Farmer
    
    with app.app_context():
        farmer = Farmer.query.filter_by(farmer_id=farmer_id).first()
        otp_record = OTPRecord.query.filter_by(farmer_id=farmer.id).order_by(OTPRecord.created_at.desc()).first()
        otp_code = otp_record.otp_code
        print(f"✅ OTP from database: {otp_code}")
    
    # Step 3: Verify OTP
    print("\n🔐 STEP 2: Verify OTP")
    response = requests.post(
        f"{BASE_URL}/api/auth/verify-otp",
        json={"farmer_id": farmer_id, "otp_code": otp_code}
    )
    print_response(response, "Verify OTP Response")
    
    if response.status_code == 200:
        farmer_data = response.json()['farmer']
        print(f"\n✅ Login Successful!")
        print(f"   Farmer: {farmer_data['name']}")
        print(f"   District: {farmer_data['district']}, {farmer_data['state']}")
        print(f"   Land: {farmer_data['total_land_area_hectares']} hectares")
    
    # Step 4: Get Profile
    print("\n📋 STEP 3: Get Profile (for Profile Page)")
    response = requests.post(f"{BASE_URL}/api/auth/profile", json={"farmer_id": farmer_id})
    print_response(response, "Get Profile Response")

def test_registration():
    """Test farmer registration"""
    print("\n📝 TEST: Farmer Registration")
    
    farmer_data = {
        "farmer_id": "987654321098",
        "name": "Priya Singh",
        "aadhaar_number": "987654321098",
        "date_of_birth": "1985-03-20",
        "gender": "F",
        "phone_number": "8765432109",
        "email": "priya@example.com",
        "caste_category": "SC",
        "permanent_address": "Village Indore, Madhya Pradesh",
        "district": "Indore",
        "taluka": "Mhow",
        "village": "Mhow",
        "state": "Madhya Pradesh",
        "pincode": "453440",
        "total_land_area_hectares": 3.0,
        "land_holder_type": "Owner",
        "soil_type": "Black Soil",
        "current_crops": "Soybean, Mustard",
        "bank_name": "HDFC Bank",
        "ifsc_code": "HDFC0001234"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=farmer_data)
    print_response(response, "Registration Response")

def main():
    print("\n" + "="*60)
    print("  🌾 Telhan Sathi Backend Test Suite")
    print("="*60)
    
    try:
        # Test OTP login flow
        test_otp_flow()
        
        # Test registration
        test_registration()
        
        print("\n" + "="*60)
        print("  ✅ All tests completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure Flask server is running: python app.py")

if __name__ == "__main__":
    main()
