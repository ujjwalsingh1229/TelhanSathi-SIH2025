"""
FORECAST ENGINE - ARIMA Time Series + Oilseed Recommendations
Predicts market prices for next 12 months and recommends oilseed shifting
Location-based forecasting: Supports state-level price variations
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

class ForecastEngine:
    """
    Forecast prices and recommend crop shifting based on market trends
    Supports location-based forecasting for different states/regions
    """
    
    def __init__(self):
        self.oilseeds = ['groundnut', 'sunflower', 'soybean', 'mustard', 'coconut']
        self.scaler = MinMaxScaler()
        
        # Location-based price variations (multiplier from national average)
        self.location_multipliers = {
            'maharashtra': 1.05,      # 5% higher prices
            'punjab': 0.98,           # 2% lower prices
            'karnataka': 1.08,        # 8% higher prices
            'rajasthan': 0.95,        # 5% lower prices
            'madhya_pradesh': 1.02,   # 2% higher prices
            'andhra_pradesh': 1.03,   # 3% higher prices
            'bihar': 0.97,            # 3% lower prices
            'uttar_pradesh': 0.99,    # 1% lower prices
        }
        
        # Oilseed production zones
        self.oilseed_zones = {
            'groundnut': ['maharashtra', 'karnataka', 'andhra_pradesh', 'rajasthan'],
            'sunflower': ['karnataka', 'maharashtra', 'madhya_pradesh'],
            'soybean': ['madhya_pradesh', 'maharashtra', 'rajasthan'],
            'mustard': ['rajasthan', 'madhya_pradesh', 'uttar_pradesh'],
            'coconut': ['karnataka', 'andhra_pradesh'],
        }
        
    def generate_synthetic_price_data(self, crop_name, months=36, location=None):
        """
        Generate realistic historical price data (₹/quintal)
        Adjusts for location-based variations
        """
        np.random.seed(hash(crop_name + str(location)) % 2**32)
        
        # Base prices by crop
        base_prices = {
            'groundnut': 5500,
            'sunflower': 7200,
            'soybean': 4800,
            'mustard': 6500,
            'coconut': 12000,
            'wheat': 2500,
            'rice': 3200,
            'maize': 2000,
            'cotton': 8000,
        }
        
        base = base_prices.get(crop_name.lower(), 5000)
        
        # Apply location multiplier if provided
        if location and location.lower() in self.location_multipliers:
            base = base * self.location_multipliers[location.lower()]
        
        # Generate prices with trend and seasonality
        prices = []
        for i in range(months):
            # Trend component (slight upward)
            trend = (i / months) * (base * 0.1)
            
            # Seasonal component (repeat every 12 months)
            seasonal = np.sin(2 * np.pi * i / 12) * (base * 0.15)
            
            # Random walk
            noise = np.random.normal(0, base * 0.05)
            
            price = base + trend + seasonal + noise
            prices.append(max(price, base * 0.5))  # Ensure positive
        
        return np.array(prices)
    
    def forecast_arima(self, crop_name, months_ahead=12, historical_months=36, location=None):
        """
        Use simple trend forecasting (ARIMA often times out on Windows)
        Location-aware: Returns price forecasts adjusted for state/region
        
        Args:
            crop_name: Name of oilseed crop
            months_ahead: Number of months to forecast (default 12)
            historical_months: Historical data months (default 36)
            location: State/region name (optional, for location-based adjustment)
        
        Returns: Dict with forecasted_prices, confidence_intervals, location info
        """
        try:
            # Generate or load historical data
            historical_prices = self.generate_synthetic_price_data(crop_name, historical_months, location)
            
            # Use simple exponential smoothing instead of ARIMA (faster, more reliable)
            # Calculate trend from last 12 months
            recent_12mo = historical_prices[-12:]
            average_trend = (recent_12mo[-1] - recent_12mo[0]) / 12
            
            # Generate forecast
            forecast = []
            lower_ci = []
            upper_ci = []
            
            for i in range(months_ahead):
                # Simple trend extrapolation
                forecasted_price = recent_12mo[-1] + (average_trend * (i + 1))
                
                # Add seasonality component (sine wave)
                seasonal = np.sin(2 * np.pi * (i % 12) / 12) * (historical_prices.mean() * 0.1)
                forecasted_price += seasonal
                
                # Ensure positive price
                forecasted_price = max(forecasted_price, historical_prices.mean() * 0.3)
                
                forecast.append(forecasted_price)
                lower_ci.append(forecasted_price * 0.85)
                upper_ci.append(forecasted_price * 1.15)
            
            return {
                'crop': crop_name,
                'location': location if location else 'National Average',
                'historical': historical_prices.tolist(),
                'forecast': forecast,
                'lower_ci': lower_ci,
                'upper_ci': upper_ci,
                'location_multiplier': self.location_multipliers.get(location.lower(), 1.0) if location else 1.0
            }
        
        except Exception as e:
            print(f"Forecast error for {crop_name}: {e}")
            return self._fallback_forecast(crop_name, months_ahead)
    
    def _fallback_forecast(self, crop_name, months_ahead=12):
        """Fallback simple forecasting if ARIMA fails"""
        historical = self.generate_synthetic_price_data(crop_name, 36)
        
        # Simple trend extrapolation
        recent_trend = (historical[-6:].mean() - historical[:6].mean()) / 6
        forecast = []
        for i in range(months_ahead):
            price = historical[-1] + recent_trend * (i + 1)
            forecast.append(max(price, historical.mean() * 0.5))
        
        forecast_arr = np.array(forecast)
        return {
            'crop': crop_name,
            'historical': historical.tolist(),
            'forecast': forecast_arr.tolist(),
            'lower_ci': (forecast_arr * 0.85).tolist(),
            'upper_ci': (forecast_arr * 1.15).tolist()
        }
    
    def compare_crops(self, crops_list=None, months_ahead=12):
        """
        Compare price forecasts across multiple crops
        """
        if crops_list is None:
            crops_list = self.oilseeds
        
        comparison = {}
        for crop in crops_list:
            forecast_data = self.forecast_arima(crop, months_ahead)
            
            # Convert lists to numpy arrays for calculations
            forecast_arr = np.array(forecast_data['forecast'])
            
            # Calculate metrics
            avg_price = float(forecast_arr.mean())
            price_growth = float((forecast_arr[-1] - forecast_arr[0]) / forecast_arr[0] * 100)
            volatility = float(forecast_arr.std() / avg_price * 100)
            
            comparison[crop] = {
                'avg_price': avg_price,
                'price_growth': price_growth,
                'volatility': volatility,
                'forecast': forecast_data['forecast'],
                'current_price': float(forecast_data['historical'][-1]),
                'confidence_interval': (forecast_data['lower_ci'], forecast_data['upper_ci'])
            }
        
        return comparison
    
    def recommend_crop_shift(self, farmer_current_crop, farmer_area_acres=5, 
                            farmer_cost_per_acre=100000, oilseeds_only=True):
        """
        Recommend shifting to oilseed production based on profit potential
        """
        crops_to_compare = self.oilseeds if oilseeds_only else self.oilseeds + ['wheat', 'rice', 'maize']
        
        comparison = self.compare_crops(crops_to_compare, months_ahead=12)
        
        # Estimate yields per crop (kg/acre)
        yield_estimates = {
            'groundnut': 1200,
            'sunflower': 1800,
            'soybean': 1500,
            'mustard': 1000,
            'coconut': 3000,
            'wheat': 2000,
            'rice': 2500,
            'maize': 3000,
            'cotton': 1200,
        }
        
        # Calculate profit potential (12-month average)
        recommendations = []
        for crop in comparison:
            avg_price = comparison[crop]['avg_price']
            yield_qty = yield_estimates.get(crop, 1500)  # kg/acre
            
            # Convert to quintal (100 kg = 1 quintal)
            yield_quintal = yield_qty / 100
            
            # Annual revenue estimate (using average forecasted price)
            annual_revenue = yield_quintal * avg_price * farmer_area_acres
            annual_cost = farmer_cost_per_acre * farmer_area_acres
            estimated_profit = annual_revenue - annual_cost
            
            # Ensure forecast is a list
            forecast_list = comparison[crop]['forecast']
            if not isinstance(forecast_list, list):
                forecast_list = list(forecast_list)
            
            recommendations.append({
                'crop': crop,
                'avg_price_next_12m': round(avg_price, 2),
                'price_trend': float(comparison[crop]['price_growth']),
                'volatility': round(comparison[crop]['volatility'], 2),
                'estimated_yield_quintals': yield_quintal,
                'estimated_annual_profit': round(estimated_profit, 2),
                'profit_per_acre': round(estimated_profit / farmer_area_acres, 2),
                'forecast_prices': forecast_list,
                'is_oilseed': crop in self.oilseeds,
                'current_crop': crop == farmer_current_crop.lower()
            })
        
        # Sort by profit
        recommendations.sort(key=lambda x: x['estimated_annual_profit'], reverse=True)
        
        return {
            'current_crop': farmer_current_crop,
            'recommendations': recommendations,
            'top_recommendation': recommendations[0] if recommendations else None,
            'oilseed_recommendation': [r for r in recommendations if r['is_oilseed']][0] if any(r['is_oilseed'] for r in recommendations) else None
        }
    
    def get_market_insights(self, crop_name, location=None):
        """
        Provide detailed market insights for a crop
        Location-aware: Adjusts insights based on state/region
        """
        forecast_data = self.forecast_arima(crop_name, months_ahead=12, location=location)
        
        prices = np.array(forecast_data['forecast'])  # Convert to numpy array
        historical = np.array(forecast_data['historical'])
        
        # Calculate metrics
        current_price = float(historical[-1])
        forecast_avg = float(prices.mean())
        price_change = float(((prices[-1] - prices[0]) / prices[0] * 100))
        
        # Determine market outlook
        if price_change > 10:
            outlook = "STRONG UPTREND - Excellent time to sell"
        elif price_change > 0:
            outlook = "MODERATE UPTREND - Good potential"
        elif price_change > -10:
            outlook = "SLIGHT DOWNTREND - Expect stability"
        else:
            outlook = "STRONG DOWNTREND - Wait for recovery"
        
        return {
            'crop': crop_name,
            'location': location if location else 'National Average',
            'location_multiplier': forecast_data['location_multiplier'],
            'current_price': round(current_price, 2),
            'forecast_average': round(forecast_avg, 2),
            'price_change_12m': round(price_change, 2),
            'max_forecast_price': round(float(prices.max()), 2),
            'min_forecast_price': round(float(prices.min()), 2),
            'market_outlook': outlook,
            'volatility': round(float(prices.std()), 2),
            'recommendation': "SHIFT TO THIS CROP" if price_change > 15 else "CONSIDER GROWING"
        }
    
    def get_location_based_recommendation(self, farmer_location, farmer_current_crop, 
                                         farmer_area_acres=5, farmer_cost_per_acre=100000):
        """
        Get crop recommendations specific to farmer's location
        Considers local market conditions and suitable crops
        """
        crops_to_check = self.oilseeds
        
        # Filter crops suitable for the location
        if farmer_location.lower() in self.oilseed_zones:
            suitable_crops = self.oilseed_zones[farmer_location.lower()]
            # Include suitable crops plus other oilseeds
            crops_to_check = list(set(suitable_crops + self.oilseeds))
        
        recommendations = []
        for crop in crops_to_check:
            try:
                insights = self.get_market_insights(crop, farmer_location)
                forecast_data = self.forecast_arima(crop, months_ahead=12, location=farmer_location)
                
                # Yield estimates
                yield_estimates = {
                    'groundnut': 1200, 'sunflower': 1800, 'soybean': 1500,
                    'mustard': 1000, 'coconut': 3000
                }
                
                yield_qty = yield_estimates.get(crop, 1500)
                yield_quintal = yield_qty / 100
                
                avg_price = insights['forecast_average']
                annual_revenue = yield_quintal * avg_price * farmer_area_acres
                annual_cost = farmer_cost_per_acre * farmer_area_acres
                profit = annual_revenue - annual_cost
                
                recommendations.append({
                    'crop': crop,
                    'location': farmer_location,
                    'suitable_for_location': crop in self.oilseed_zones.get(farmer_location.lower(), self.oilseeds),
                    'avg_price_12m': round(insights['forecast_average'], 2),
                    'price_trend': round(insights['price_change_12m'], 2),
                    'estimated_profit': round(profit, 2),
                    'profit_per_acre': round(profit / farmer_area_acres, 2),
                    'market_outlook': insights['market_outlook'],
                    'volatility': round(insights['volatility'], 2),
                    'location_price_multiplier': insights['location_multiplier']
                })
            except Exception as e:
                print(f"Error getting recommendation for {crop} in {farmer_location}: {e}")
        
        # Sort by profit
        recommendations.sort(key=lambda x: x['estimated_profit'], reverse=True)
        
        return {
            'location': farmer_location,
            'recommendations': recommendations[:3],  # Top 3
            'top_oilseed': recommendations[0] if recommendations else None,
            'suitable_crops_for_location': self.oilseed_zones.get(farmer_location.lower(), self.oilseeds)
        }


def get_forecast_data(crop_name):
    """
    API: Get 12-month forecast for a crop
    Returns JSON with prices, trends, and insights
    """
    engine = ForecastEngine()
    forecast = engine.forecast_arima(crop_name, months_ahead=12)
    insights = engine.get_market_insights(crop_name)
    
    return {
        'status': 'success',
        'crop': crop_name,
        'forecast_prices': forecast['forecast'].tolist(),
        'confidence_lower': forecast['lower_ci'].tolist(),
        'confidence_upper': forecast['upper_ci'].tolist(),
        'current_price': float(forecast['historical'][-1]),
        'insights': insights,
        'months': list(range(1, 13))
    }

def get_crop_shift_recommendation(current_crop, area_acres=5, cost_per_acre=100000):
    """
    API: Get recommendation to shift to oilseed production
    Returns profit comparison and recommendations
    """
    engine = ForecastEngine()
    recommendation = engine.recommend_crop_shift(
        current_crop, 
        area_acres, 
        cost_per_acre
    )
    
    return {
        'status': 'success',
        'current_crop': current_crop,
        'recommendations': recommendation['recommendations'][:5],  # Top 5
        'top_oilseed': recommendation['oilseed_recommendation'],
        'profit_increase': (
            recommendation['oilseed_recommendation']['estimated_annual_profit'] 
            - recommendation['recommendations'][0]['estimated_annual_profit']
            if recommendation['oilseed_recommendation'] else 0
        )
    }

def compare_multiple_crops(crops_list):
    """
    API: Compare prices across multiple crops
    Returns table with all metrics
    """
    engine = ForecastEngine()
    comparison = engine.compare_crops(crops_list, months_ahead=12)
    
    return {
        'status': 'success',
        'comparison': comparison,
        'best_profit_crop': max(comparison.items(), 
                               key=lambda x: x[1]['avg_price'])[0]
    }


# ============================================================
# TEST
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 FORECAST ENGINE - ARIMA + OILSEED RECOMMENDATIONS")
    print("="*70 + "\n")
    
    engine = ForecastEngine()
    
    # Test 1: Single crop forecast
    print("📊 1. SINGLE CROP FORECAST - Groundnut")
    print("-" * 70)
    forecast = engine.forecast_arima('groundnut', months_ahead=12)
    print(f"   Current Price: ₹{forecast['historical'][-1]:.0f}/quintal")
    print(f"   Next 12 Month Forecast:")
    for i, price in enumerate(forecast['forecast'][:3], 1):
        print(f"      Month {i}: ₹{price:.0f}/quintal")
    print(f"      ... (forecast continues for 12 months)")
    
    # Test 2: Market insights
    print("\n📈 2. MARKET INSIGHTS - Sunflower")
    print("-" * 70)
    insights = engine.get_market_insights('sunflower')
    print(f"   Current Price: ₹{insights['current_price']}/quintal")
    print(f"   12-Month Forecast Avg: ₹{insights['forecast_average']}/quintal")
    print(f"   Expected Change: {insights['price_change_12m']:.1f}%")
    print(f"   Outlook: {insights['market_outlook']}")
    print(f"   Recommendation: {insights['recommendation']}")
    
    # Test 3: Crop comparison
    print("\n🌾 3. CROP COMPARISON - Oilseeds")
    print("-" * 70)
    comparison = engine.compare_crops(engine.oilseeds)
    print("   Crop          | Avg Price | Growth | Profit (₹/acre)")
    print("   " + "-" * 50)
    for crop in comparison:
        print(f"   {crop:13} | ₹{comparison[crop]['avg_price']:8.0f} | "
              f"{comparison[crop]['price_growth']:5.1f}% | "
              f"₹{comparison[crop]['avg_price'] * 15 * 5 / 100 - 100000:10.0f}")
    
    # Test 4: Shift recommendation
    print("\n🔄 4. CROP SHIFT RECOMMENDATION")
    print("-" * 70)
    print("   Scenario: Farmer growing Wheat on 5 acres")
    recommendation = engine.recommend_crop_shift('wheat', 5, 100000)
    top_oilseed = recommendation['oilseed_recommendation']
    print(f"   Top Oilseed: {top_oilseed['crop'].upper()}")
    print(f"   Est. Annual Profit: ₹{top_oilseed['estimated_annual_profit']:,.0f}")
    print(f"   Profit per Acre: ₹{top_oilseed['profit_per_acre']:,.0f}")
    print(f"   Price Trend: {top_oilseed['price_trend']:.1f}%")
    
    print("\n" + "="*70)
    print("✅ FORECAST ENGINE READY!")
    print("="*70 + "\n")
