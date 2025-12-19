# 🚀 GETTING STARTED - Farmer Dashboard Backend

Welcome! This guide will get you up and running in 10 minutes.

## What Is This?

A **complete backend system** for comparing crop profitability. Farmers input crop parameters, and the system calculates profits, forecasts next year, and recommends which crop to grow.

**3 API Endpoints:**
- `POST /api/predict-profit` - Compare profits
- `POST /api/forecast-arima` - 12-month forecast
- `POST /api/recommend-crop` - Get recommendation

---

## 📋 Prerequisites

You need:
- **Python 3.7+** ([Download](https://www.python.org/downloads/))
- **Git** (optional, for cloning)
- **Command line/Terminal** access
- **Text editor** (VS Code, Notepad++, etc.)

Check you have Python:
```bash
python --version
# Should show: Python 3.7.x or higher
```

---

## ⚡ 10-Minute Quick Start

### Step 1: Get the Code (1 min)

**Option A: Download ZIP**
- Click "Code" → "Download ZIP"
- Extract to your computer

**Option B: Git Clone**
```bash
git clone <repository-url> farmer-dashboard
cd farmer-dashboard/FARMER_DASHBOARD_BACKEND
```

### Step 2: Create Virtual Environment (2 min)

Windows:
```cmd
python -m venv venv
venv\Scripts\activate
```

Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal now.

### Step 3: Install Dependencies (3 min)

```bash
pip install -r requirements.txt
```

Wait for installation to complete. You'll see many packages installing.

### Step 4: Create Database (2 min)

Windows:
```cmd
sqlite3 farmer_dashboard.db < database_schema.sql
```

Mac/Linux:
```bash
sqlite3 farmer_dashboard.db < database_schema.sql
```

Or if that doesn't work:
```bash
python -c "import sqlite3; sqlite3.connect('farmer_dashboard.db')"
```

### Step 5: Start Server (1 min)

```bash
python app.py
```

You should see:
```
========================================
Farmer Profit Comparison Dashboard
========================================

Starting Flask server...

Available Endpoints:
- POST http://localhost:5000/api/predict-profit
- POST http://localhost:5000/api/forecast-arima
- POST http://localhost:5000/api/recommend-crop

========================================
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to stop
```

✅ **Server is running!**

---

## 🧪 Test It Out

Open **another terminal** (keep the server running) and test the API:

### Test 1: Health Check
```bash
curl http://localhost:5000/
```

Should return:
```json
{
  "status": "ok",
  "service": "Farmer Profit Comparison Dashboard",
  "version": "1.0.0"
}
```

### Test 2: Calculate Profit (Predict Endpoint)

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

Should return profit comparison between Soybean and Maize!

---

## 📚 File Overview

| File | Purpose |
|------|---------|
| `app.py` | Main Flask server - START HERE |
| `flask_integration.py` | API endpoints |
| `profit_calculator.py` | Profit math |
| `arima_forecaster.py` | 12-month forecasting |
| `recommendation_engine.py` | Crop recommendation |
| `config.py` | Settings |
| `utils.py` | Helper functions |
| `database_schema.sql` | Database tables |
| `test_endpoints.py` | Tests (run with pytest) |
| `requirements.txt` | Python packages needed |

---

## 🔧 Common Tasks

### Run Tests
```bash
python -m pytest test_endpoints.py -v
```

### Stop Server
Press `Ctrl+C` in the terminal where server is running

### Deactivate Virtual Environment
```bash
deactivate
```

### View Logs
Check the terminal where `python app.py` is running

---

## 🚀 What to Do Next

### Option 1: Explore the Code
1. Read `INDEX.md` - Navigation guide
2. Read `README.md` - Quick reference
3. Look at `test_endpoints.py` - See example requests

### Option 2: Integrate into Flask App
```python
from flask import Flask
from flask_integration import register_dashboard_routes

app = Flask(__name__)
register_dashboard_routes(app)  # Adds 3 endpoints
app.run()
```

### Option 3: Use in Your Own Code
```python
from profit_calculator import calculate_profit_metrics
from arima_forecaster import forecast_profits

metrics = calculate_profit_metrics({
    'land_area': 2,
    'expected_yield': 2000,
    'market_price': 60,
    'total_cost_per_hectare': 45000
})

print(f"Net Profit: ₹{metrics['net_profit']}")
print(f"ROI: {metrics['roi']}%")
```

---

## 💡 Understanding the System

### Profit Calculation

```
Input: Soybean, 2 hectares, 2000 kg/ha, ₹60/kg, ₹45,000/ha cost

Calculation:
  Total Yield = 2000 kg/ha × 2 ha = 4,000 kg
  Revenue = 4,000 kg × ₹60/kg = ₹240,000
  Cost = ₹45,000/ha × 2 ha = ₹90,000
  Net Profit = ₹240,000 - ₹90,000 = ₹150,000
  
Output:
  Profit: ₹150,000 ✓
  ROI: 166.67%
  Margin: 62.5%
```

### 5-Factor Recommendation

The system scores each crop on:
1. **Net Profit** (30%) - How much money you make
2. **ROI** (25%) - Return on investment
3. **Profit Margin** (20%) - Percentage profit
4. **Cultivation Ease** (15%) - How hard to grow (1-10)
5. **Forecast Stability** (10%) - How predictable future profits

**Total Score: 0-10 points**

Example: Maize scores 8.5/10 → Recommended!

### 12-Month Forecast

Uses ARIMA model to predict:
```
Month 1: ₹150,000 (can be ₹98k to ₹202k with 95% confidence)
Month 2: ₹155,000 (can be ₹101k to ₹209k)
...
Month 12: ₹185,000 (can be ₹120k to ₹250k)

Average: ₹157,545
Stability: Medium (good for planning)
```

---

## ❓ Frequently Asked Questions

### Q: What if I get "ModuleNotFoundError"?
**A:** Run `pip install -r requirements.txt` again

### Q: Can I change the crop parameters?
**A:** Yes! Edit `config.py` - all settings are there

### Q: How do I add a new crop?
**A:** Add to `CULTIVATION_FACTORS` dict in `config.py` or `recommendation_engine.py`

### Q: Where is the database?
**A:** `farmer_dashboard.db` in the same folder as `app.py`

### Q: Can I use PostgreSQL instead of SQLite?
**A:** Yes! Update DATABASE_URI in `config.py` to: `postgresql://user:password@localhost/farmer_dashboard`

### Q: How do I deploy to production?
**A:** See `DEPLOYMENT_GUIDE.md`

### Q: What if the server won't start?
**A:** 
1. Check port 5000 is free: `netstat -tulpn | grep 5000`
2. Check Python version: `python --version` (need 3.7+)
3. Check dependencies: `pip install -r requirements.txt`

---

## 📖 Documentation Map

Start here based on your need:

**Just Getting Started:**
- This file (`GETTING_STARTED.md`) ← You are here

**Quick Reference:**
- `README.md` - 5-min overview
- `INDEX.md` - Finding things

**Feature Overview:**
- `SUMMARY.md` - What's included

**Complete Guide:**
- `COMPLETE_README.md` - Full reference
- `DEPLOYMENT_GUIDE.md` - Production deployment

**Code Examples:**
- `test_endpoints.py` - See working examples
- Each `.py` file has docstrings

**Configuration:**
- `config.py` - All settings with comments

**Database:**
- `database_schema.sql` - 3 tables + views

---

## 🎯 Example Workflow

1. **User inputs crop parameters** (web form)
   ```json
   {
     "oilseed_name": "Soybean",
     "oilseed_area": 2,
     "oilseed_yield": 2000,
     ...
   }
   ```

2. **System calculates profit** via `/api/predict-profit`
   ```json
   {
     "oilseed_net_profit": 150000,
     "crop_net_profit": 178000,
     ...
   }
   ```

3. **System forecasts** via `/api/forecast-arima`
   ```json
   {
     "oilseed_forecast": [
       {"month": 1, "prediction": 95000, ...},
       ...
     ],
     ...
   }
   ```

4. **System recommends** via `/api/recommend-crop`
   ```json
   {
     "recommended_crop": "Maize",
     "recommendation_score": 8.5,
     "reasoning": ["Higher profit", "Better ROI", ...]
   }
   ```

5. **Farmer sees results** and makes decision!

---

## 🆘 Need Help?

### Issues During Installation?
1. Check Python version: `python --version` (need 3.7+)
2. Reinstall dependencies: `pip install -r requirements.txt --upgrade`
3. Clear cache: `pip cache purge`
4. Check internet connection

### Server Won't Start?
1. Check port 5000 is available
2. Try different port: Edit `app.py`, change `port=5000` to `port=8000`
3. Check error message in terminal

### Tests Failing?
1. Run `pip install -r requirements.txt` again
2. Ensure database file exists: `ls farmer_dashboard.db`
3. Check Python version

### Need More Help?
1. Check `COMPLETE_README.md` for detailed docs
2. Look at `test_endpoints.py` for examples
3. Review `config.py` for configuration options
4. Read docstrings in each Python file

---

## ✅ Success Checklist

- [ ] Python 3.7+ installed
- [ ] Code downloaded
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Database initialized
- [ ] Server started successfully
- [ ] Health check works (curl localhost:5000)
- [ ] Can run tests (pytest)

**If all checked ✓, you're ready to use the system!**

---

## 🎓 Next Learning Steps

### Beginner:
- Test all 3 endpoints with sample data
- Read `INDEX.md`
- Try modifying configuration

### Intermediate:
- Integrate into your Flask app
- Add new crops to database
- Customize scoring weights

### Advanced:
- Modify ARIMA model parameters
- Add database caching
- Deploy to production (see `DEPLOYMENT_GUIDE.md`)

---

## 📞 Quick Reference

**Important Files:**
- `app.py` - Server startup
- `config.py` - All settings
- `test_endpoints.py` - Examples

**Key Commands:**
- Start: `python app.py`
- Test: `python -m pytest test_endpoints.py -v`
- Install: `pip install -r requirements.txt`

**API Endpoints:**
- Profit: `POST http://localhost:5000/api/predict-profit`
- Forecast: `POST http://localhost:5000/api/forecast-arima`
- Recommend: `POST http://localhost:5000/api/recommend-crop`

---

## 🎉 You're All Set!

The system is ready to use. Choose your next step:

1. **Explore**: Read `INDEX.md`
2. **Integrate**: Add to your Flask app
3. **Deploy**: Follow `DEPLOYMENT_GUIDE.md`
4. **Customize**: Edit `config.py`

**Happy farming! 🌾**

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Production Ready ✅
