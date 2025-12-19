#!/usr/bin/env python
import urllib.request
import json

print("Testing /api/forecast/groundnut...")
try:
    response = urllib.request.urlopen("http://localhost:5000/api/forecast/groundnut", timeout=5)
    data = json.loads(response.read().decode())
    print(f"Status code: {response.status}")
    print(f"Response keys: {data.keys()}")
    print(f"Status field: {data.get('status')}")
    print(f"Crop field: {data.get('crop')}")
    print(f"Current price: {data.get('current_price')}")
    print(f"Forecast prices: {len(data.get('forecast_prices', []))} items")
    if 'error' in data:
        print(f"ERROR in response: {data['error']}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
