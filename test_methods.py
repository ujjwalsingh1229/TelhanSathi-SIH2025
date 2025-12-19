#!/usr/bin/env python
import sys
sys.path.insert(0, 'c:\\Users\\ujju1\\Desktop\\SIH_PROJECT')

try:
    from forecast_engine import ForecastEngine
    
    engine = ForecastEngine()
    print("[Testing] get_market_insights...")
    insights = engine.get_market_insights('soybean')
    print("[OK] Market insights work")
    print(f"Outlook: {insights['market_outlook']}")
    print(f"Price change: {insights['price_change_12m']}%")
    
    print("\n[Testing] compare_crops...")
    comparison = engine.compare_crops(['soybean', 'groundnut'])
    print("[OK] Compare crops works")
    print(f"Soybean avg price: {comparison['soybean']['avg_price']}")
    
    print("\n[Testing] recommend_crop_shift...")
    recommendation = engine.recommend_crop_shift('wheat', 5, 100000)
    print("[OK] Recommendations work")
    print(f"Top recommended: {recommendation['recommendations'][0]['crop']}")
    print(f"Profit: Rs {recommendation['recommendations'][0]['estimated_annual_profit']}")
    
    print("\n[PASS] All forecast engine methods working!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
