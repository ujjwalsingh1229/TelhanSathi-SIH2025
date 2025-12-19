#!/usr/bin/env python
import json

try:
    print("Testing yield prediction API...")
    
    import sys
    sys.path.insert(0, 'c:\\Users\\ujju1\\Desktop\\SIH_PROJECT')
    
    from app import app
    
    client = app.test_client()
    
    # Test predict endpoint
    payload = {
        "Crop": "soybean",
        "State": "maharashtra",
        "District": "pune",
        "Soil": "black",
        "Season": "kharif",
        "Area": 5.0,
        "Annual_Rainfall": 1200,
        "Fertilizer": 80000,
        "Pesticide": 1000,
        "N": 90,
        "P": 40,
        "K": 40,
        "temperature": 28,
        "humidity": 70,
        "Crop_Year": 2025,
        "Price_per_kg": 3500,
        "Total_Cost": 250000,
        "Date": "2025-06-01"
    }
    
    print("[Testing] POST /api/predict...")
    response = client.post('/api/predict', 
                          data=json.dumps(payload),
                          content_type='application/json')
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("[OK] Yield prediction API works")
        result = response.get_json()
        print(f"Predicted yield: {result.get('predicted_yield', 'N/A')}")
    else:
        print(f"[ERROR] Status {response.status_code}")
        print(f"Response: {response.data.decode()}")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
