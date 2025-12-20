"""
FARMER PROFIT DASHBOARD - Flask Web Application
Simple, farmer-friendly yield prediction and profit calculation
+ ARIMA Forecast Engine + Oilseed Recommendations
"""

from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
from forecast_engine import ForecastEngine
from forecast_dashboard_enhanced import create_forecast_dashboard_routes, ENHANCED_DASHBOARD_HTML

# ============================================================
# CONFIGURATION
# ============================================================
MODEL_PATH = "yield_prediction_model.pkl"
FEATURE_IMPORTANCE_PATH = "feature_importance.csv"

app = Flask(__name__)

# ============================================================
# LOAD MODEL AT STARTUP
# ============================================================
print("[*] Starting Farmer Profit Dashboard...")

if not os.path.exists(MODEL_PATH):
    print(f"[ERROR] {MODEL_PATH} not found!")
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

if not os.path.exists(FEATURE_IMPORTANCE_PATH):
    print(f"[ERROR] {FEATURE_IMPORTANCE_PATH} not found!")
    raise FileNotFoundError(f"Feature file not found: {FEATURE_IMPORTANCE_PATH}")

# Load the trained model
model = joblib.load(MODEL_PATH)
print(f"[OK] Model loaded successfully")

# Get feature columns from model
if hasattr(model, 'feature_names_in_'):
    FEATURE_COLUMNS = list(model.feature_names_in_)
    print(f"[OK] Features from model: {len(FEATURE_COLUMNS)} columns")
else:
    # Fallback to CSV
    feature_df = pd.read_csv(FEATURE_IMPORTANCE_PATH)
    FEATURE_COLUMNS = feature_df["Feature"].tolist()
    print(f"[OK] Features from CSV: {len(FEATURE_COLUMNS)} columns")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def infer_season_from_month(month: int) -> str:
    """Map month number to Indian agricultural season."""
    if month in [6, 7, 8, 9, 10]:  # Jun-Oct
        return "kharif"
    elif month in [11, 12, 1, 2, 3]:  # Nov-Mar
        return "rabi"
    elif month in [4, 5]:  # Apr-May
        return "summer"
    return "whole year"


def preprocess_single_row(input_dict: dict) -> pd.DataFrame:
    """
    Convert user input to model-ready format.
    Handles categorical encoding and feature alignment.
    """
    try:
        # Create a copy to avoid modifying input
        row = input_dict.copy()
        
        # String fields - lowercase and strip whitespace
        for field in ['Crop', 'State', 'Season']:
            if field in row and isinstance(row[field], str):
                row[field] = row[field].strip().lower()
        
        # Create DataFrame with single row
        df = pd.DataFrame([row])
        
        # One-hot encode categorical columns
        categorical_cols = ['Crop', 'State', 'Season']
        df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=False)
        
        # Align with model's expected features
        df_aligned = df_encoded.reindex(columns=FEATURE_COLUMNS, fill_value=0)
        
        return df_aligned
        
    except Exception as e:
        print(f"[ERROR] Preprocessing error: {e}")
        raise ValueError(f"Failed to preprocess input: {str(e)}")


def calculate_profit(yield_kg, price_per_kg, area_ha, cost_per_ha):
    """Calculate farm profit metrics."""
    total_yield = yield_kg * area_ha
    total_revenue = total_yield * price_per_kg
    total_cost = cost_per_ha * area_ha
    net_profit = total_revenue - total_cost
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    roi = (net_profit / total_cost * 100) if total_cost > 0 else 0
    profit_per_kg = net_profit / total_yield if total_yield > 0 else 0
    
    return {
        "total_yield_kg": round(total_yield, 2),
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "net_profit": round(net_profit, 2),
        "profit_margin_percent": round(profit_margin, 2),
        "roi_percent": round(roi, 2),
        "profit_per_kg": round(profit_per_kg, 2)
    }


# ============================================================
# HTML FORM TEMPLATE
# ============================================================
HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Farmer Profit Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 28px;
            margin-bottom: 5px;
        }
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        .form-container {
            padding: 40px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 10px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .results {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 6px;
            display: none;
        }
        .results.show {
            display: block;
        }
        .metric {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }
        .metric-item {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }
        .metric-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
            text-transform: uppercase;
        }
        .metric-value {
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }
        .success { border-left-color: #4caf50; }
        .info { border-left-color: #2196f3; }
        .warning { border-left-color: #ff9800; }
        .error {
            color: #d32f2f;
            padding: 15px;
            background: #ffebee;
            border-radius: 6px;
            margin-top: 20px;
            display: none;
        }
        .error.show {
            display: block;
        }
        .info-box {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
            font-size: 14px;
            color: #1565c0;
        }
        @media (max-width: 600px) {
            .form-row {
                grid-template-columns: 1fr;
            }
            .metric {
                grid-template-columns: 1fr;
            }
            .header h1 {
                font-size: 22px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌾 Farmer Profit Dashboard</h1>
            <p>Know your crop profit before planting</p>
        </div>
        
        <div class="form-container">
            <div class="info-box">
                ℹ️ Enter your crop details and get instant profit prediction
            </div>
            
            <form id="predictForm">
                <h3 style="margin-bottom: 20px; color: #333;">📋 Your Farm Details</h3>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="crop">Crop Name</label>
                        <select id="crop" name="Crop" required>
                            <option value="">-- Select Crop --</option>
                            <option value="Rice">Rice</option>
                            <option value="Wheat">Wheat</option>
                            <option value="Maize">Maize</option>
                            <option value="Soybean">Soybean</option>
                            <option value="Groundnut">Groundnut</option>
                            <option value="Cotton">Cotton</option>
                            <option value="Sugarcane">Sugarcane</option>
                            <option value="Potato">Potato</option>
                            <option value="Onion">Onion</option>
                            <option value="Tomato">Tomato</option>
                            <option value="Mustard">Mustard</option>
                            <option value="Sunflower">Sunflower</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="state">State</label>
                        <select id="state" name="State" required>
                            <option value="">-- Select State --</option>
                            <option value="Maharashtra">Maharashtra</option>
                            <option value="Karnataka">Karnataka</option>
                            <option value="Gujarat">Gujarat</option>
                            <option value="Madhya Pradesh">Madhya Pradesh</option>
                            <option value="Rajasthan">Rajasthan</option>
                            <option value="Punjab">Punjab</option>
                            <option value="Haryana">Haryana</option>
                            <option value="Uttar Pradesh">Uttar Pradesh</option>
                            <option value="West Bengal">West Bengal</option>
                            <option value="Andhra Pradesh">Andhra Pradesh</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="district">District</label>
                        <select id="district" name="district" required>
                            <option value="">-- Select District --</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="soiltype">Soil Type</label>
                        <select id="soiltype" name="soiltype" required>
                            <option value="">-- Select Soil Type --</option>
                            <option value="Black Soil">Black Soil (Cotton, Sugarcane)</option>
                            <option value="Red Soil">Red Soil (Groundnut, Millets)</option>
                            <option value="Alluvial">Alluvial (Rice, Wheat)</option>
                            <option value="Loamy">Loamy (Vegetables, Pulses)</option>
                            <option value="Sandy">Sandy (Millets, Groundnut)</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="season">Season</label>
                        <select id="season" name="Season" required>
                            <option value="">-- Select Season --</option>
                            <option value="kharif">Kharif (Jun-Oct) - Monsoon crops</option>
                            <option value="rabi">Rabi (Nov-Mar) - Winter crops</option>
                            <option value="zaid">Zaid (Apr-May) - Summer crops</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="area">Land Size (Acres)</label>
                        <input type="number" id="area" name="Area" step="0.25" min="0.25" placeholder="e.g., 2.5" required>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="sowing">Sowing Date (When you planted)</label>
                        <input type="date" id="sowing" name="sowing_date" required>
                    </div>
                    <div class="form-group">
                        <label for="price">Market Price (₹/kg)</label>
                        <input type="number" id="price" name="price_per_kg" step="0.5" min="1" placeholder="e.g., 50" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="cost">Total Cost Spent (₹)</label>
                    <input type="number" id="cost" name="cost_total" step="100" min="100" placeholder="e.g., 45000" required>
                </div>
                
                <button type="submit">📊 Calculate Expected Profit</button>
            </form>
            
            <div class="error" id="errorMsg"></div>
            
            <div class="results" id="results">
                <h3 style="margin-bottom: 20px; color: #333;">📈 Your Profit Analysis</h3>
                
                <div class="metric">
                    <div class="metric-item success">
                        <div class="metric-label">Total Yield</div>
                        <div class="metric-value" id="totalYield">-</div>
                    </div>
                    <div class="metric-item info">
                        <div class="metric-label">Yield per Acre</div>
                        <div class="metric-value" id="yieldPerAcre">-</div>
                    </div>
                </div>
                
                <div class="metric">
                    <div class="metric-item info">
                        <div class="metric-label">Total Revenue</div>
                        <div class="metric-value" id="totalRevenue">-</div>
                    </div>
                    <div class="metric-item info">
                        <div class="metric-label">Total Cost</div>
                        <div class="metric-value" id="totalCost">-</div>
                    </div>
                </div>
                
                <div class="metric">
                    <div class="metric-item success">
                        <div class="metric-label">Net Profit</div>
                        <div class="metric-value" id="netProfit">-</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">Profit per Acre</div>
                        <div class="metric-value" id="profitPerAcre">-</div>
                    </div>
                </div>
                
                <div class="metric">
                    <div class="metric-item">
                        <div class="metric-label">Profit Margin</div>
                        <div class="metric-value" id="margin">-</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">Return on Investment</div>
                        <div class="metric-value" id="roi">-</div>
                    </div>
                </div>
                
                <div class="metric">
                    <div class="metric-item success">
                        <div class="metric-label">Profit per Quintal</div>
                        <div class="metric-value" id="profitPerQuintal">-</div>
                    </div>
                    <div class="metric-item info">
                        <div class="metric-label">Predicted Yield</div>
                        <div class="metric-value" id="predictedYield">-</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Districts for each state
        const stateDistricts = {
            'Maharashtra': ['Pune', 'Mumbai', 'Nashik', 'Aurangabad', 'Nagpur', 'Kolhapur', 'Sangli', 'Solapur', 'Buldhana', 'Akola'],
            'Karnataka': ['Bengaluru', 'Belagavi', 'Dharwad', 'Tumkur', 'Kolar', 'Mysuru', 'Mandya', 'Hassan', 'Chikmangalur', 'Kodagu'],
            'Gujarat': ['Ahmedabad', 'Vadodara', 'Surat', 'Rajkot', 'Bhavnagar', 'Junagadh', 'Jamnagar', 'Kutch', 'Kheda', 'Anand'],
            'Madhya Pradesh': ['Indore', 'Bhopal', 'Gwalior', 'Jabalpur', 'Ujjain', 'Sagar', 'Khargone', 'Nimar', 'Morena', 'Rewa'],
            'Rajasthan': ['Jaipur', 'Jodhpur', 'Ajmer', 'Bikaner', 'Pali', 'Barmer', 'Nagaur', 'Sikar', 'Churu', 'Ganganagar'],
            'Punjab': ['Amritsar', 'Ludhiana', 'Jalandhar', 'Patiala', 'Hoshiarpur', 'Ferozepur', 'Bhatinda', 'Sangrur', 'Mansa', 'Kapurthala'],
            'Haryana': ['Hisar', 'Rohtak', 'Ambala', 'Yamunanagar', 'Karnal', 'Panipat', 'Sonipat', 'Jind', 'Faridabad', 'Gurgaon'],
            'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Agra', 'Varanasi', 'Meerut', 'Saharanpur', 'Bareilly', 'Moradabad', 'Mathura', 'Aligarh'],
            'West Bengal': ['Kolkata', 'Howrah', 'Darjeeling', 'Jalpaiguri', 'Birbhum', 'Murshidabad', 'Nadia', 'South 24 Parganas', 'North 24 Parganas', 'Bardhaman'],
            'Andhra Pradesh': ['Hyderabad', 'Visakhapatnam', 'Vijayawada', 'Guntur', 'Krishna', 'Nellore', 'Prakasam', 'Chittoor', 'Kadapa', 'Warangal']
        };

        // Update districts when state changes
        document.getElementById('state').addEventListener('change', function() {
            const state = this.value;
            const districtSelect = document.getElementById('district');
            
            // Clear and reset district dropdown
            districtSelect.innerHTML = '<option value="">-- Select District --</option>';
            
            if (state && stateDistricts[state]) {
                stateDistricts[state].forEach(district => {
                    const option = document.createElement('option');
                    option.value = district;
                    option.textContent = district;
                    districtSelect.appendChild(option);
                });
            }
        });

        // Form submission
        document.getElementById('predictForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const errorMsg = document.getElementById('errorMsg');
            errorMsg.classList.remove('show');
            
            // Convert acres to hectares (1 acre = 0.4047 hectares)
            const areaAcres = parseFloat(document.getElementById('area').value);
            const areaHectares = areaAcres * 0.4047;
            
            // Convert total cost to cost per hectare
            const costTotal = parseFloat(document.getElementById('cost').value);
            const costPerHectare = costTotal / areaHectares;
            
            // Get default weather values based on season
            const season = document.getElementById('season').value;
            let rainfall = 1200, temperature = 28, humidity = 70;
            
            if (season === 'kharif') {
                rainfall = 1200; temperature = 28; humidity = 70;
            } else if (season === 'rabi') {
                rainfall = 400; temperature = 22; humidity = 65;
            } else if (season === 'zaid') {
                rainfall = 200; temperature = 35; humidity = 55;
            }
            
            const formData = {
                Crop: document.getElementById('crop').value,
                State: document.getElementById('state').value,
                Crop_Year: new Date().getFullYear(),
                Area: areaHectares,
                Annual_Rainfall: rainfall,
                Fertilizer: 80000,
                Pesticide: 1000,
                N: 90,
                P: 40,
                K: 40,
                temperature: temperature,
                humidity: humidity,
                price_per_kg: parseFloat(document.getElementById('price').value),
                cost_per_ha: costPerHectare,
                Season: season
            };
            
            try {
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Prediction failed');
                }
                
                // Display results
                const totalYieldQuintals = (data.profit_metrics.total_yield_kg / 100);
                const yieldPerAcre = (data.predicted_yield * 0.4047) / 100;  // kg/ha to quintal/acre
                const profitPerAcre = data.profit_metrics.net_profit / areaAcres;
                const profitPerQuintal = data.profit_metrics.net_profit / totalYieldQuintals;
                
                document.getElementById('totalYield').textContent = 
                    totalYieldQuintals.toLocaleString('en-IN', {maximumFractionDigits: 2}) + ' quintals';
                document.getElementById('yieldPerAcre').textContent = 
                    yieldPerAcre.toFixed(2) + ' quintal/acre';
                document.getElementById('totalRevenue').textContent = 
                    '₹' + (data.profit_metrics.total_revenue).toLocaleString();
                document.getElementById('totalCost').textContent = 
                    '₹' + costTotal.toLocaleString();
                document.getElementById('netProfit').textContent = 
                    '₹' + (data.profit_metrics.net_profit).toLocaleString();
                document.getElementById('profitPerAcre').textContent = 
                    '₹' + profitPerAcre.toLocaleString('en-IN', {maximumFractionDigits: 0});
                document.getElementById('margin').textContent = 
                    data.profit_metrics.profit_margin_percent.toFixed(1) + '%';
                document.getElementById('roi').textContent = 
                    data.profit_metrics.roi_percent.toFixed(1) + '%';
                document.getElementById('profitPerQuintal').textContent = 
                    '₹' + profitPerQuintal.toFixed(2) + '/quintal';
                document.getElementById('predictedYield').textContent = 
                    data.predicted_yield.toFixed(0) + ' kg/hectare';
                
                document.getElementById('results').classList.add('show');
                
            } catch (error) {
                errorMsg.textContent = '❌ Error: ' + error.message;
                errorMsg.classList.add('show');
            }
        });
    </script>
</body>
</html>
"""


# ============================================================
# API ROUTES
# ============================================================

@app.route('/')
def home():
    """Render the main form."""
    return render_template_string(HTML_FORM)


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    API endpoint for yield prediction and profit calculation.
    
    Expected JSON:
    {
        "Crop": "soybean",
        "State": "maharashtra",
        "Crop_Year": 2024,
        "Area": 2.5,
        "Season": "kharif",
        "Annual_Rainfall": 1200,
        "Fertilizer": 80000,
        "Pesticide": 1000,
        "N": 90,
        "P": 40,
        "K": 40,
        "temperature": 28,
        "humidity": 70,
        "price_per_kg": 50,
        "cost_per_ha": 45000
    }
    """
    try:
        data = request.get_json()
        
        # Extract user inputs
        price_per_kg = data.get('price_per_kg', 50)
        area_ha = data.get('Area', 1)
        cost_per_ha = data.get('cost_per_ha', 40000)
        
        # Prepare ALL data for model prediction (all features required)
        model_input = {
            'Crop': data.get('Crop', 'rice'),
            'State': data.get('State', 'maharashtra'),
            'Crop_Year': data.get('Crop_Year', 2024),
            'Area': area_ha,
            'Season': data.get('Season', 'kharif'),
            'Annual_Rainfall': data.get('Annual_Rainfall', 1200),
            'Fertilizer': data.get('Fertilizer', 80000),
            'Pesticide': data.get('Pesticide', 1000),
            'N': data.get('N', 90),
            'P': data.get('P', 40),
            'K': data.get('K', 40),
            'temperature': data.get('temperature', 28),
            'humidity': data.get('humidity', 70)
        }
        
        # Preprocess and predict yield using ML model
        X = preprocess_single_row(model_input)
        predicted_yield = float(model.predict(X)[0])
        
        # Calculate profit metrics using PREDICTED yield (not user input)
        profit_metrics = calculate_profit(
            yield_kg=predicted_yield,  # USE PREDICTED YIELD
            price_per_kg=price_per_kg,
            area_ha=area_ha,
            cost_per_ha=cost_per_ha
        )
        
        return jsonify({
            'status': 'success',
            'predicted_yield': round(predicted_yield, 2),
            'crop': data.get('Crop', 'rice'),
            'state': data.get('State', 'maharashtra'),
            'input_params': model_input,
            'profit_metrics': profit_metrics,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'app': 'Farmer Profit Dashboard',
        'features': len(FEATURE_COLUMNS),
        'timestamp': datetime.now().isoformat()
    })


# ============================================================
# ERROR HANDLERS
# ============================================================

# ============================================================
# FORECAST ENGINE - ARIMA + OILSEED RECOMMENDATIONS
# ============================================================

# Initialize forecast engine
forecast_engine = ForecastEngine()

# Import forecast dashboard UI
from forecast_dashboard_ui import FORECAST_DASHBOARD_HTML

@app.route('/forecast')
def forecast_dashboard():
    """
    Forecast dashboard with ARIMA charts and recommendations
    """
    return render_template_string(FORECAST_DASHBOARD_HTML)

@app.route('/api/forecast/<crop_name>', methods=['GET'])
def forecast_crop(crop_name):
    """
    Get 12-month price forecast for a crop using ARIMA
    Location-aware: Supports state/region-based price variations
    Query params: location (optional)
    Returns: prices, trends, and market insights
    """
    try:
        location = request.args.get('location', None)  # Get location from query params
        forecast_data = forecast_engine.forecast_arima(crop_name, months_ahead=12, location=location)
        insights = forecast_engine.get_market_insights(crop_name, location=location)
        
        return jsonify({
            'status': 'success',
            'crop': crop_name,
            'location': location if location else 'National Average',
            'current_price': round(float(forecast_data['historical'][-1]), 2),
            'forecast_prices': [round(float(p), 2) for p in forecast_data['forecast']],
            'confidence_lower': [round(float(p), 2) for p in forecast_data['lower_ci']],
            'confidence_upper': [round(float(p), 2) for p in forecast_data['upper_ci']],
            'location_multiplier': forecast_data['location_multiplier'],
            'insights': insights,
            'months': list(range(1, 13))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommend-crop-shift', methods=['POST'])
def recommend_crop_shift():
    """
    Get oilseed crop shift recommendations
    Input: current_crop, area_acres, cost_per_acre
    Returns: Top crops to shift to with profit estimates
    """
    try:
        data = request.get_json()
        current_crop = data.get('current_crop', 'wheat')
        area_acres = float(data.get('area_acres', 5))
        cost_per_acre = float(data.get('cost_per_acre', 100000))
        
        recommendation = forecast_engine.recommend_crop_shift(
            current_crop, 
            area_acres, 
            cost_per_acre,
            oilseeds_only=True
        )
        
        return jsonify({
            'status': 'success',
            'current_crop': current_crop,
            'area_acres': area_acres,
            'top_recommendations': recommendation['recommendations'][:3],
            'top_oilseed': recommendation['oilseed_recommendation']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare-crops', methods=['POST'])
def compare_crops_endpoint():
    """
    Compare prices across multiple crops
    Input: crops list
    Returns: Comparison table with all metrics
    """
    try:
        data = request.get_json()
        crops_list = data.get('crops', ['groundnut', 'sunflower', 'soybean', 'mustard'])
        
        comparison = forecast_engine.compare_crops(crops_list, months_ahead=12)
        
        # Format for JSON
        comparison_formatted = {}
        for crop, metrics in comparison.items():
            comparison_formatted[crop] = {
                'avg_price': round(metrics['avg_price'], 2),
                'price_growth': round(metrics['price_growth'], 2),
                'volatility': round(metrics['volatility'], 2),
                'current_price': round(metrics['current_price'], 2)
            }
        
        return jsonify({
            'status': 'success',
            'comparison': comparison_formatted,
            'best_profit_crop': max(comparison.items(), 
                                   key=lambda x: x[1]['avg_price'])[0]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/market-insights', methods=['GET'])
def market_insights():
    """
    Get market insights for all oilseeds
    Returns: Detailed analysis for each crop
    """
    try:
        oilseeds = ['groundnut', 'sunflower', 'soybean', 'mustard', 'coconut']
        insights_all = {}
        
        for crop in oilseeds:
            insights = forecast_engine.get_market_insights(crop)
            insights_all[crop] = insights
        
        return jsonify({
            'status': 'success',
            'insights': insights_all,
            'oilseeds': oilseeds
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/location-based-forecast', methods=['POST'])
def location_based_forecast():
    """
    Get location-specific crop recommendations and forecasts
    Input: location, current_crop, area_acres, cost_per_acre
    Returns: Recommendations tailored to the farmer's location
    """
    try:
        data = request.get_json()
        location = data.get('location', '').lower()
        current_crop = data.get('current_crop', 'wheat')
        area_acres = float(data.get('area_acres', 5))
        cost_per_acre = float(data.get('cost_per_acre', 100000))
        
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        
        # Get location-based recommendations
        recommendation = forecast_engine.get_location_based_recommendation(
            location,
            current_crop,
            area_acres,
            cost_per_acre
        )
        
        return jsonify({
            'status': 'success',
            'location': location,
            'current_crop': current_crop,
            'recommendations': recommendation['recommendations'],
            'top_oilseed': recommendation['top_oilseed'],
            'suitable_crops': recommendation['suitable_crops_for_location']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/forecast-by-location/<crop_name>/<location>', methods=['GET'])
def forecast_by_location(crop_name, location):
    """
    Get forecast for a specific crop in a specific location
    Path params: crop_name, location
    Returns: Location-adjusted price forecast
    """
    try:
        forecast_data = forecast_engine.forecast_arima(crop_name, months_ahead=12, location=location)
        insights = forecast_engine.get_market_insights(crop_name, location=location)
        
        return jsonify({
            'status': 'success',
            'crop': crop_name,
            'location': location,
            'current_price': round(float(forecast_data['historical'][-1]), 2),
            'forecast_prices': [round(float(p), 2) for p in forecast_data['forecast']],
            'confidence_lower': [round(float(p), 2) for p in forecast_data['lower_ci']],
            'confidence_upper': [round(float(p), 2) for p in forecast_data['upper_ci']],
            'location_multiplier': forecast_data['location_multiplier'],
            'insights': insights,
            'months': list(range(1, 13))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================
# MAIN
# ============================================================

# Register enhanced forecast dashboard routes
create_forecast_dashboard_routes(app)

if __name__ == "__main__":
    print(f"[OK] Dashboard ready!")
    print(f"[INFO] Yield Prediction: http://localhost:5000")
    print(f"[INFO] Forecast (Old): http://localhost:5000/forecast")
    print(f"[INFO] Enhanced Forecast Dashboard: http://localhost:5000/forecast-dashboard")
    print(f"[INFO] Press CTRL+C to stop\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
