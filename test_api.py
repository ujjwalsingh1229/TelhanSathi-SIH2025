#!/usr/bin/env python
import traceback
import sys

try:
    print("Testing forecast engine...")
    from forecast_engine import ForecastEngine
    
    engine = ForecastEngine()
    print("[OK] ForecastEngine initialized")
    
    print("Calling forecast_arima('soybean')...")
    result = engine.forecast_arima('soybean')
    print("[OK] ARIMA forecast works")
    print(f"Forecast keys: {result.keys()}")
    print(f"Forecast type: {type(result['forecast'])}")
    print(f"Forecast values: {result['forecast'][:3]}")
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    traceback.print_exc()
    import sys
    sys.exit(1)

print("[OK] All tests passed!")
