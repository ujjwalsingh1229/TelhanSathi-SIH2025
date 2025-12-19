# Farmer Profit Comparison Dashboard - Backend Package

## Overview

This backend package provides a production-ready Python module system for the Farmer Profit Comparison Dashboard. It enables farmers to make data-driven decisions by comparing oil seed profitability against alternative crops using profit metrics, ROI analysis, cultivation difficulty assessment, and ARIMA-based profit forecasting.

**Key Features:**
- Profit calculation and comparison engine
- ARIMA time-series forecasting with 95% confidence intervals
- 5-factor weighted recommendation scoring system
- 14-crop cultivation difficulty database
- Flask REST API with 3 endpoints
- Comprehensive testing suite
- Production-ready database schema
- Input validation and error handling

## Quick Start

### 1. Installation

```bash
cd FARMER_DASHBOARD_BACKEND
pip install flask pandas numpy statsmodels scikit-learn
```

### 2. Initialize Database

```bash
sqlite3 farmer_dashboard.db < database_schema.sql
```

### 3. Start Flask Server

```bash
python app.py
# Server runs on http://localhost:5000
```

### 4. Run Tests

```bash
python -m pytest test_endpoints.py -v
python -m pytest test_endpoints.py --cov=. --cov-report=html
```

## Package Structure

```
FARMER_DASHBOARD_BACKEND/
├── profit_calculator.py         # Core profit calculation (100 lines)
├── arima_forecaster.py          # ARIMA forecasting (120 lines)
├── recommendation_engine.py     # 5-factor scoring (220 lines)
├── flask_integration.py         # 3 API endpoints (250 lines)
├── config.py                    # All parameters (350 lines)
├── utils.py                     # Utility functions (300 lines)
├── database_schema.sql          # Database tables & views (250 lines)
├── test_endpoints.py            # Unit tests (400+ lines)
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## API Endpoints

### 1. POST `/api/predict-profit`

Calculate profit metrics and compare two crops

**Request:**
```json
{
  "oilseed_name": "Soybean",
  "oilseed_area": 2,
  "oilseed_yield": 2000,
  "oilseed_price": 60,
  "oilseed_cost": 45000,
  "crop_name": "Maize",
  "crop_area": 2,
  "crop_yield": 5000,
  "crop_price": 25,
  "crop_cost": 36000
}
```

**Response:**
```json
{
  "success": true,
  "oilseed": {
    "name": "Soybean",
    "total_yield": 4000,
    "total_revenue": 240000,
    "total_cost": 90000,
    "net_profit": 150000,
    "profit_margin": 62.5,
    "roi": 166.67,
    "profit_per_kg": 37.5
  },
  "crop": {
    "name": "Maize",
    "total_yield": 10000,
    "total_revenue": 250000,
    "total_cost": 72000,
    "net_profit": 178000,
    "profit_margin": 71.16,
    "roi": 247.22,
    "profit_per_kg": 17.8
  },
  "comparison": {
    "more_profitable": "Maize",
    "profit_difference": 28000,
    "roi_difference": 80.55,
    "percentage_better": "18.67%"
  }
}
```

**Calculations:**
- Total Yield = Expected Yield × Land Area (kg)
- Total Revenue = Total Yield × Market Price (₹)
- Total Cost = Cost Per Hectare × Land Area (₹)
- Net Profit = Total Revenue - Total Cost (₹)
- Profit Margin = (Net Profit / Revenue) × 100 (%)
- ROI = (Net Profit / Cost) × 100 (%)

### 2. POST `/api/forecast-arima`

Generate 12-month profit forecast with 95% confidence intervals

**Request:**
```json
{
  "oilseed_name": "Soybean",
  "oilseed_base_profit": 150000,
  "crop_name": "Maize",
  "crop_base_profit": 178000,
  "forecast_months": 12,
  "arima_order": [1, 1, 1]
}
```

**Response:**
```json
{
  "success": true,
  "oilseed_forecast": {
    "name": "Soybean",
    "forecast": [
      {
        "period": 1,
        "predicted_profit": 95000,
        "confidence_lower": 45000,
        "confidence_upper": 145000
      }
    ],
    "average_12month": 105115,
    "forecast_std": 35000,
    "aic": 532.64
  },
  "crop_forecast": {
    "name": "Maize",
    "forecast": [],
    "average_12month": 157545,
    "forecast_std": 42000,
    "aic": 543.42
  },
  "comparison": {
    "more_stable": "oilseed",
    "stability_ratio": 1.2
  }
}
```

**Forecast Details:**
- ARIMA(1,1,1) model trained on 24 months synthetic data
- 95% confidence intervals (α=0.05)
- Stability measured by forecast standard deviation
- AIC score for model comparison

### 3. POST `/api/recommend-crop`

Get comprehensive crop recommendation with 5-factor scoring

**Request:** (same as /api/predict-profit)

**Response:**
```json
{
  "success": true,
  "recommendation": "Maize",
  "recommendation_score": 8.5,
  "alternative_score": 2.0,
  "score_margin": 6.5,
  "benefits": {
    "net_profit": "₹178,000",
    "roi": "247.22%",
    "profit_margin": "71.16%",
    "difficulty": "3/10"
  },
  "estimated_12month_avg": "₹157,545",
  "reasoning": [
    "✅ 18.67% higher net profit",
    "✅ Better ROI: 247.22% vs 166.67%",
    "✅ Higher profit margin: 71.16%",
    "✅ Easier cultivation (difficulty: 3/10)",
    "✅ More stable profit forecast"
  ],
  "score_breakdown": {
    "net_profit": {
      "oilseed": 0.0,
      "crop": 3.0,
      "factor": "Net Profit",
      "weight": 0.3
    }
  }
}
```

**Scoring System (Total: 10 points):**
| Factor | Weight | Max Points | Description |
|--------|--------|-----------|-------------|
| Net Profit | 30% | 3.0 | Higher profit wins |
| ROI | 25% | 2.5 | Better ROI wins |
| Profit Margin | 20% | 2.0 | Higher margin wins |
| Cultivation Ease | 15% | 1.5 | Lower difficulty wins |
| Forecast Stability | 10% | 1.0 | Lower variance wins |

## Module Documentation

### profit_calculator.py (100 lines)

**Core Functions:**

```python
calculate_profit_metrics(crop_dict) → dict
  Input: {'land_area', 'expected_yield', 'market_price', 'total_cost_per_hectare'}
  Output: All profit metrics with validation
  
compare_crops(oilseed_metrics, crop_metrics) → dict
  Returns: Comparison with profit/ROI differences
  
validate_crop_input(crop_dict) → (bool, str)
  Returns: (is_valid, error_message)
  
format_currency(amount) → str
  Example: 150000 → "₹150,000"
  
format_percentage(value) → str
  Example: 62.5 → "62.50%"
```

### arima_forecaster.py (120 lines)

**Core Functions:**

```python
train_arima_model(historical_data, order=(1,1,1)) → ARIMA model
  Input: 24+ months of profit data
  Output: Fitted ARIMA model with AIC score
  
forecast_profits(fitted_model, periods=12) → dict
  Output: 12-month forecast with 95% confidence intervals
  
generate_seasonal_historical_data(base_profit, months=24, season) → np.array
  Creates synthetic 24-month data with seasonal patterns
  
get_forecast_confidence_summary(forecast_data) → dict
  Returns: Risk level, mean, min, max forecasts
  
compare_forecast_stability(forecast_1, forecast_2) → dict
  Returns: More stable crop, stability ratio
```

**ARIMA Model Specifications:**
- Order: (1, 1, 1)
  - p=1: AR(1) autoregressive component
  - d=1: First differencing for stationarity
  - q=1: MA(1) moving average component
- Confidence Level: 95% (α=0.05)
- Training Data: 24 months minimum
- Forecast Horizon: 12 months

### recommendation_engine.py (220 lines)

**Core Functions:**

```python
generate_recommendation(metrics_os, metrics_cp, data_os, data_cp,
                       ease_os, ease_cp, forecast_os, forecast_cp) → scores, reasons
  
get_cultivation_ease(crop_name) → dict
  Returns: Difficulty (1-10), water requirement, labor, pests, market access
  
calculate_recommendation_score_breakdown(...) → dict
  Detailed breakdown of each scoring factor
  
format_recommendation_output(...) → dict
  Formatted for API response with all metadata
```

**Cultivation Difficulty Database (14 crops):**

| Crop | Difficulty | Water | Labor | Pests | Market |
|------|-----------|-------|-------|-------|--------|
| Soybean | 4 | Moderate | Low-Mod | Moderate | High |
| Groundnut | 5 | Low | Moderate | High | High |
| Mustard | 3 | Low | Low | Low | High |
| Sunflower | 4 | Moderate | Low | Moderate | High |
| Sesame | 5 | Low | Moderate | Moderate | Medium |
| Castor | 3 | Low | Low | Low | Medium |
| Linseed | 3 | Low | Low | Low | Medium |
| Rapeseed | 3 | Low | Low | Low | Medium |
| Safflower | 4 | Low | Low | Moderate | Low |
| Niger Seed | 3 | Low | Low | Low | Low |
| Maize | 3 | High | Moderate | High | High |
| Wheat | 2 | Low | Low | Low | High |
| Rice | 6 | Very High | High | High | High |
| Cotton | 7 | High | High | Very High | High |

### flask_integration.py (250 lines)

**Flask Blueprint Setup:**

```python
from flask import Flask
from flask_integration import register_dashboard_routes

app = Flask(__name__)
register_dashboard_routes(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

**Features:**
- 3 REST endpoints (POST)
- Input validation on all requests
- Structured JSON responses
- Comprehensive error handling
- CORS-ready blueprint architecture

### config.py (350 lines)

**Configuration Sections:**

1. **ARIMA Forecasting** - Model order, periods, confidence level
2. **Recommendation Scoring** - 5-factor weights, score interpretation
3. **Cultivation Factors** - 14-crop database
4. **Input Validation** - Min/max constraints for each field
5. **Database** - Connection strings, table names
6. **API Settings** - Response formatting, pagination
7. **Security** - Input sanitization, CORS
8. **Currency Formatting** - Symbol, decimal places, separators
9. **Default Values** - Per-crop parameters
10. **Feature Flags** - Enable/disable functionality
11. **Performance** - Caching, batch sizes

### utils.py (300 lines)

**Formatting Functions:**
- `format_currency(amount)` - ₹ formatting
- `format_percentage(value)` - % formatting
- `format_json_date(date_obj)` - ISO date strings

**Validation Functions:**
- `sanitize_string(value)` - Remove special characters
- `sanitize_number(value, min, max)` - Bounds checking
- `validate_crop_input_values(crop_data)` - Field validation

**Calculation Functions:**
- `calculate_percentage_change(old, new)` - Change %
- `calculate_roi(profit, cost)` - ROI %
- `calculate_profit_margin(revenue, profit)` - Margin %
- `get_risk_level(std, mean)` - Risk assessment

**Response Functions:**
- `create_error_response(message, code)` - Standardized errors
- `create_success_response(data, message)` - Standardized success

## Database Schema

### farmer_inputs (Primary Table)
Stores farmer input parameters for crop comparison
```sql
CREATE TABLE farmer_inputs (
  input_id PRIMARY KEY,
  created_at, updated_at,
  farmer_name, farmer_email, farmer_location,
  oilseed_name, oilseed_area, oilseed_yield, oilseed_price, oilseed_cost,
  crop_name, crop_area, crop_yield, crop_price, crop_cost,
  notes, is_archived
)
Indexes: farmer_name, crops, created_at
```

### profit_results (Results Table)
Stores calculated profit metrics and comparison
```sql
CREATE TABLE profit_results (
  result_id PRIMARY KEY,
  input_id FOREIGN KEY,
  created_at, updated_at,
  oilseed_metrics (8 fields),
  crop_metrics (8 fields),
  comparison (3 fields),
  recommended_crop, recommendation_score
)
Indexes: input_id, created_at, recommended_crop
```

### forecast_results (Forecast Table)
Stores 12-month ARIMA forecasts with CI
```sql
CREATE TABLE forecast_results (
  forecast_id PRIMARY KEY,
  result_id FOREIGN KEY,
  created_at, updated_at,
  oilseed_monthly_forecasts (36 fields: 12 months × 3 values),
  oilseed_summary (3 fields: average, std, aic),
  crop_monthly_forecasts (36 fields),
  crop_summary (3 fields),
  comparison (2 fields),
  confidence_level
)
Indexes: result_id, created_at
```

### Views (3 Pre-built Queries)
- `latest_profit_results` - Most recent comparison per farmer
- `profit_comparison_summary` - Aggregated crop comparisons
- `forecast_stability_summary` - Historical forecast stability

## Integration with Existing Flask App

### Option 1: Include as Blueprint

```python
from flask import Flask
from FARMER_DASHBOARD_BACKEND.flask_integration import register_dashboard_routes

app = Flask(__name__)

# Register existing routes
@app.route('/home')
def home():
    return 'Existing app'

# Register dashboard routes
register_dashboard_routes(app)

app.run()
```

### Option 2: Standalone Microservice

```bash
# Run as separate service on port 5001
FLASK_APP=FARMER_DASHBOARD_BACKEND/flask_integration.py
FLASK_PORT=5001
flask run
```

### Option 3: Import Modules Directly

```python
from FARMER_DASHBOARD_BACKEND.profit_calculator import calculate_profit_metrics
from FARMER_DASHBOARD_BACKEND.arima_forecaster import train_arima_model, forecast_profits
from FARMER_DASHBOARD_BACKEND.recommendation_engine import generate_recommendation

# Use functions in your own code
metrics = calculate_profit_metrics(crop_data)
forecast = forecast_profits(model, periods=12)
recommendation = generate_recommendation(...)
```

## Testing

### Run All Tests
```bash
python -m pytest test_endpoints.py -v
python -m pytest test_endpoints.py::TestProfitCalculator -v
python -m pytest test_endpoints.py::TestFlaskAPI -v
```

### Test Coverage Report
```bash
python -m pytest test_endpoints.py --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

### Sample Test Payloads

**cURL - Predict Profit:**
```bash
curl -X POST http://localhost:5000/api/predict-profit \
  -H "Content-Type: application/json" \
  -d '{
    "oilseed_name": "Soybean",
    "oilseed_area": 2,
    "oilseed_yield": 2000,
    "oilseed_price": 60,
    "oilseed_cost": 45000,
    "crop_name": "Maize",
    "crop_area": 2,
    "crop_yield": 5000,
    "crop_price": 25,
    "crop_cost": 36000
  }'
```

**cURL - Forecast:**
```bash
curl -X POST http://localhost:5000/api/forecast-arima \
  -H "Content-Type: application/json" \
  -d '{
    "oilseed_name": "Soybean",
    "oilseed_base_profit": 150000,
    "crop_name": "Maize",
    "crop_base_profit": 178000,
    "forecast_months": 12
  }'
```

**cURL - Recommend:**
```bash
curl -X POST http://localhost:5000/api/recommend-crop \
  -H "Content-Type: application/json" \
  -d '{
    "oilseed_name": "Soybean",
    "oilseed_area": 2,
    "oilseed_yield": 2000,
    "oilseed_price": 60,
    "oilseed_cost": 45000,
    "crop_name": "Maize",
    "crop_area": 2,
    "crop_yield": 5000,
    "crop_price": 25,
    "crop_cost": 36000
  }'
```

## Configuration Guide

### ARIMA Parameters

```python
# config.py
ARIMA_ORDER = (1, 1, 1)              # p=1, d=1, q=1
FORECAST_PERIODS = 12                 # 12-month ahead
CONFIDENCE_LEVEL = 0.05               # 95% confidence (1-alpha)
TRAINING_MONTHS = 24                  # Minimum 12, recommended 24
```

### Scoring Weights

```python
SCORING_WEIGHTS = {
    'net_profit': 0.30,        # 3.0 points max
    'roi': 0.25,               # 2.5 points max
    'profit_margin': 0.20,     # 2.0 points max
    'cultivation_ease': 0.15,  # 1.5 points max
    'forecast_stability': 0.10 # 1.0 point max
}
# Total: 10.0 points
```

### Input Constraints

```python
INPUT_CONSTRAINTS = {
    'land_area': {'min': 0.01, 'max': 100},           # hectares
    'expected_yield': {'min': 0, 'max': 50000},       # kg/hectare
    'market_price': {'min': 0, 'max': 1000},          # ₹/kg
    'total_cost_per_hectare': {'min': 0, 'max': 500000} # ₹
}
```

## Deployment Checklist

- [ ] Clone repository and navigate to FARMER_DASHBOARD_BACKEND/
- [ ] Create Python 3.7+ virtual environment
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Initialize database: `sqlite3 farmer_dashboard.db < database_schema.sql`
- [ ] Review and update config.py for production settings
- [ ] Run complete test suite: `pytest test_endpoints.py -v`
- [ ] Verify all 3 endpoints respond correctly with test payloads
- [ ] Configure database backups (daily minimum)
- [ ] Set up application logging and monitoring
- [ ] Enable CORS if frontend is on different domain
- [ ] Deploy with WSGI server (Gunicorn, uWSGI, etc.)
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall and API rate limiting
- [ ] Monitor forecast accuracy against actual results
- [ ] Document any customizations or modifications

## Security Considerations

**Input Validation:**
- All numeric fields validated for min/max bounds
- String fields sanitized to prevent injection
- Unknown crops default to standard cultivation factors

**Error Handling:**
- Errors returned without sensitive information
- Stack traces only logged, not returned to client
- Invalid requests return 400 with clear error message

**Database:**
- SQL injection prevented via SQLAlchemy parameterization
- Foreign key constraints enforced
- Timestamps automatically maintained

**API Security:**
- Recommend: HTTPS only in production
- Rate limiting: 100 requests per 60 seconds
- CORS: Configure for specific domains only
- Input size limits: 100 characters for strings

## Performance Optimization

**Caching Strategy:**
- Cache cultivation factors database (never changes)
- Cache seasonal patterns for same season/base_profit
- 1-hour TTL for forecast results

**Database Indexing:**
- farmer_name (frequent filters)
- crop_name (common queries)
- created_at (sorting, date range queries)
- input_id (foreign key joins)

**API Optimization:**
- Forecast calculation runs async for large requests
- Batch multiple comparisons in single request
- Use pagination for result lists (default: 20 per page)

**Model Training:**
- ARIMA training cached for 24-hour period
- Synthetic data generation pre-cached per crop
- Model selection (AIC) cached across requests

## Production Deployment with Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 worker processes
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With logging
gunicorn -w 4 -b 0.0.0.0:5000 --log-level info app:app

# Via systemd service (Linux)
[Service]
ExecStart=/usr/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
WorkingDirectory=/path/to/FARMER_DASHBOARD_BACKEND
```

## Version Information

- **Backend Version**: 1.0.0
- **Python**: 3.7+
- **Dependencies**: pandas, numpy, statsmodels, flask, scikit-learn
- **Database**: SQLite3 (or PostgreSQL for production)

## Support Resources

- Documentation: See README files in each module
- Tests: Run test_endpoints.py for examples
- Examples: Sample payloads provided in cURL format
- Configuration: All parameters in config.py with documentation
- Database: Schema and views in database_schema.sql

## License & Attribution

Farmer Dashboard Backend Package v1.0
Designed for agricultural decision support systems
© 2024 SIH Project Team
