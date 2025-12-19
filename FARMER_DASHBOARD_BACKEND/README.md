# 🌾 Farmer Profit Comparison Dashboard - Backend Package

**For Backend Developer Integration**

---

## 📦 Package Contents

This folder contains all necessary components for integrating the Farmer Profit Comparison Dashboard with your backend/Flask API:

```
FARMER_DASHBOARD_BACKEND/
├── README.md (this file)
├── API_ENDPOINTS.md (Complete endpoint documentation)
├── requirements.txt (Python dependencies)
├── profit_calculator.py (Core profit calculation module)
├── arima_forecaster.py (ARIMA time-series forecasting module)
├── recommendation_engine.py (Multi-factor recommendation algorithm)
├── database_schema.sql (Database schema for storing results)
├── flask_integration.py (Flask route examples)
├── test_endpoints.py (Unit tests for all endpoints)
├── utils.py (Helper functions)
└── config.py (Configuration settings)
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Copy Modules to Your Project
```bash
# Copy the Python modules to your Flask app directory
cp *.py /path/to/your/flask/app/modules/
```

### 3. Integrate Flask Routes
```python
# In your main Flask app file (app.py)
from modules.flask_integration import register_dashboard_routes

# Register dashboard routes
register_dashboard_routes(app)
```

### 4. Test the Endpoints
```bash
python test_endpoints.py
```

---

## 📊 API Endpoints Summary

### 1. **POST /api/predict-profit**
Calculate instant profit metrics for crop comparison

**Input:**
```json
{
  "crop_name": "soybean",
  "land_area": 2.0,
  "oilseed_yield": 2000,
  "oilseed_price": 60,
  "oilseed_cost": 45000,
  "alternative_crop": "maize",
  "crop_yield": 5000,
  "crop_price": 25,
  "crop_cost": 36000
}
```

**Output:**
```json
{
  "oilseed": {
    "name": "soybean",
    "total_profit": 150000,
    "roi": 166.67,
    "profit_margin": 62.5
  },
  "traditional_crop": {
    "name": "maize",
    "total_profit": 178000,
    "roi": 247.22,
    "profit_margin": 71.2
  },
  "comparison": {
    "more_profitable": "maize",
    "difference": 28000
  }
}
```

---

### 2. **POST /api/forecast-arima**
Generate 12-month ARIMA profit forecasts with confidence intervals

**Input:**
```json
{
  "crop_name": "soybean",
  "historical_profits": [157000, 170000, 198000, ...],
  "forecast_months": 12
}
```

**Output:**
```json
{
  "crop": "soybean",
  "forecast": [
    {
      "month": "2024-01",
      "predicted_profit": 105567,
      "lower_ci": 61334,
      "upper_ci": 149801
    }
  ],
  "average_forecast": 105115
}
```

---

### 3. **POST /api/recommend-crop**
Get AI-powered crop recommendation based on multi-factor analysis

**Input:**
```json
{
  "crop_name": "soybean",
  "alternative_crop": "maize",
  "oilseed_profit": 150000,
  "crop_profit": 178000,
  "oilseed_difficulty": 4,
  "crop_difficulty": 3
}
```

**Output:**
```json
{
  "recommended_crop": "maize",
  "recommendation_score": 10.0,
  "scoring_breakdown": {
    "net_profit": 3.0,
    "roi": 2.5,
    "profit_margin": 2.0,
    "cultivation_ease": 1.5,
    "forecast_stability": 1.0
  },
  "reasoning": [
    "18.7% higher net profit",
    "Better ROI: 247.2% vs 166.7%",
    "Easier cultivation"
  ]
}
```

---

## 🔧 Module Documentation

### `profit_calculator.py`
**Purpose:** Calculate profit metrics instantly

**Main Functions:**
- `calculate_profit_metrics(crop_dict)` - Returns revenue, cost, profit, ROI, margin
- `compare_crops(oilseed_data, crop_data)` - Side-by-side comparison

**Usage:**
```python
from profit_calculator import calculate_profit_metrics

crop_data = {
    'land_area': 2.0,
    'expected_yield': 2000,
    'market_price': 60,
    'total_cost_per_hectare': 45000
}

metrics = calculate_profit_metrics(crop_data)
print(f"Net Profit: ₹{metrics['net_profit']:,.0f}")
```

---

### `arima_forecaster.py`
**Purpose:** ARIMA time-series forecasting with 95% confidence intervals

**Main Functions:**
- `train_arima_model(historical_data)` - Train ARIMA(1,1,1) model
- `forecast_profits(model, periods=12)` - Generate future predictions

**Usage:**
```python
from arima_forecaster import train_arima_model, forecast_profits

historical_profits = [157000, 170000, 198000, ...]  # 24 months
model = train_arima_model(historical_profits)
forecast = forecast_profits(model, periods=12)
```

---

### `recommendation_engine.py`
**Purpose:** Multi-factor scoring algorithm for crop recommendations

**Main Functions:**
- `generate_recommendation(oilseed_metrics, crop_metrics, ...)` - Calculate recommendation score
- `get_cultivation_ease(crop_name)` - Lookup cultivation difficulty

**Scoring Weights:**
- Net Profit: 30%
- ROI: 25%
- Profit Margin: 20%
- Cultivation Ease: 15%
- Forecast Stability: 10%

**Usage:**
```python
from recommendation_engine import generate_recommendation

score_os, score_cp, reasons_os, reasons_cp = generate_recommendation(
    oilseed_metrics, crop_metrics, oilseed_data, crop_data,
    oilseed_ease, crop_ease, forecast_os, forecast_cp
)

if score_os > score_cp:
    print(f"Recommend: {oilseed_data['name']}")
```

---

## 🗄️ Database Schema

Three main tables for storing farmer data and results:

```sql
-- Farmer input data
CREATE TABLE farmer_inputs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    farmer_id INT NOT NULL,
    crop_name VARCHAR(50),
    land_area FLOAT,
    expected_yield INT,
    market_price FLOAT,
    total_cost INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Profit calculation results
CREATE TABLE profit_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    farmer_id INT NOT NULL,
    oilseed_name VARCHAR(50),
    oilseed_profit INT,
    crop_name VARCHAR(50),
    crop_profit INT,
    recommendation VARCHAR(50),
    recommendation_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id)
);

-- ARIMA forecast results
CREATE TABLE forecast_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    result_id INT NOT NULL,
    forecast_month VARCHAR(10),
    predicted_profit INT,
    confidence_lower INT,
    confidence_upper INT,
    FOREIGN KEY (result_id) REFERENCES profit_results(id)
);
```

---

## 🧪 Testing

### Run Unit Tests
```bash
python test_endpoints.py
```

### Test Individual Endpoints
```bash
# Test profit calculation
curl -X POST http://localhost:5000/api/predict-profit \
  -H "Content-Type: application/json" \
  -d @sample_payload.json

# Test forecasting
curl -X POST http://localhost:5000/api/forecast-arima \
  -H "Content-Type: application/json" \
  -d @forecast_payload.json

# Test recommendation
curl -X POST http://localhost:5000/api/recommend-crop \
  -H "Content-Type: application/json" \
  -d @recommendation_payload.json
```

---

## 📝 Configuration

Edit `config.py` to customize:

```python
# Model settings
ARIMA_ORDER = (1, 1, 1)  # ARIMA(p,d,q) parameters
FORECAST_PERIODS = 12     # Number of months to forecast
CONFIDENCE_LEVEL = 0.05   # 95% confidence interval

# Scoring weights
PROFIT_WEIGHT = 0.30
ROI_WEIGHT = 0.25
MARGIN_WEIGHT = 0.20
EASE_WEIGHT = 0.15
STABILITY_WEIGHT = 0.10

# Cultivation factors
CULTIVATION_FACTORS = {
    'Soybean': {'difficulty': 4, 'water': 'Moderate', ...},
    'Maize': {'difficulty': 3, 'water': 'High', ...},
    # ... more crops
}
```

---

## 🔐 Security Considerations

1. **Input Validation**
   - All inputs validated before processing
   - Type checking for numeric values
   - Crop name validation against known crops

2. **Error Handling**
   - Try-catch blocks for ARIMA model training
   - Graceful fallbacks for missing data
   - Detailed error messages for debugging

3. **API Rate Limiting** (Recommended)
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app)
   @app.route('/api/predict-profit')
   @limiter.limit("10 per minute")
   def predict_profit():
       ...
   ```

---

## 📊 Performance Optimization

1. **Caching ARIMA Models**
   ```python
   @functools.lru_cache(maxsize=100)
   def get_arima_model(crop_name):
       return joblib.load(f'models/arima_{crop_name}.pkl')
   ```

2. **Database Indexing**
   ```sql
   CREATE INDEX idx_farmer_id ON farmer_inputs(farmer_id);
   CREATE INDEX idx_crop_name ON farmer_inputs(crop_name);
   ```

3. **Async Processing** (for heavy forecasts)
   ```python
   from celery import Celery
   
   @app.route('/api/forecast-arima')
   def forecast_arima():
       task = forecast_task.delay(crop_name, historical_data)
       return {'task_id': task.id}
   ```

---

## 🚀 Deployment Checklist

- [ ] Install all dependencies from `requirements.txt`
- [ ] Configure database connection in `config.py`
- [ ] Run database schema creation (`database_schema.sql`)
- [ ] Test all endpoints with `test_endpoints.py`
- [ ] Set up error logging and monitoring
- [ ] Configure CORS if needed for frontend access
- [ ] Set up rate limiting for production
- [ ] Deploy with WSGI server (Gunicorn/uWSGI)
- [ ] Monitor API performance and response times
- [ ] Set up automated backups for results

---

## 📞 Support & Integration Help

### File: `INTEGRATION_GUIDE.md`
Complete step-by-step guide for integrating all components

### File: `API_ENDPOINTS.md`
Detailed documentation for each endpoint with examples

### File: `test_endpoints.py`
Ready-to-use test cases for all endpoints

---

## 📈 Next Steps

1. ✅ Copy all files to your backend project
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Import modules in Flask app
4. ✅ Register routes: `register_dashboard_routes(app)`
5. ✅ Test with: `python test_endpoints.py`
6. ✅ Deploy to production

---

## 📦 Version Info

- **Version:** 1.0.0
- **Created:** December 2025
- **Python Version:** 3.7+
- **Key Dependencies:** pandas, numpy, statsmodels, flask, joblib

---

**For questions or issues, refer to API_ENDPOINTS.md and INTEGRATION_GUIDE.md**

