**Purpose**: Guidance for AI coding agents working on this farmer-focused agricultural decision support system.

**Project Overview**: 
A two-tier Flask application with dual dashboards for yield prediction and price forecasting. Root `app.py` serves the Farmer Profit Dashboard with web UI; `FARMER_DASHBOARD_BACKEND/` contains a separate modular API with advanced features (ARIMA forecasting, crop recommendations). Both share ML models but operate independently.

**Architecture Tiers**:
1. **Root-level (`app.py`)**: Full-stack farmer dashboard—web form, ML inference, profit calculations. Single Flask app with embedded HTML/CSS/JS.
2. **Backend module (`FARMER_DASHBOARD_BACKEND/`)**: Structured API server with separate concerns—config, forecasting, profit/recommendation engines. Extensible but less directly deployed.

**Key Files & Responsibilities**:
- **`app.py`** (828 lines, canonical): Form rendering (HTML_FORM template), core `/api/predict` endpoint, preprocessing (`preprocess_single_row`), profit calc, season mapping. **Read this first.**
- **`forecast_engine.py`**: ARIMA forecasting fallback (Windows-friendly trend extrapolation), synthetic price data generation for oilseeds.
- **`feature_importance.csv`**: Sacred artifact—lists exact one-hot encoded columns (108 features) model expects. Order matters for `reindex()`.
- **`yield_prediction_model.pkl`**: RandomForest, 106 features, loads via `joblib` at startup. Must have `feature_names_in_` or fallback to CSV.
- **`FARMER_DASHBOARD_BACKEND/config.py`**: ARIMA tuning (p,d,q), season mappings, cultivation difficulty weights, scoring thresholds.
- **`FARMER_DASHBOARD_BACKEND/flask_integration.py`**: Routes registry, decouples API endpoints from main app entry point.

**Data Flow—Single Prediction**:
```
Form Input → preprocess_single_row() 
  → lowercase/strip Crop/State/Season 
  → pd.get_dummies() [one-hot] 
  → reindex(columns=FEATURE_COLUMNS, fill_value=0) [align to model] 
  → model.predict() [RandomForest] 
  → calculate_profit() [farmer metrics] 
  → HTML response
```

**Categorical Encoding Contract**:
- **Crops**: soybean, wheat, rice, maize, cotton, groundnut (see `feature_importance.csv` lines 1–6)
- **States**: maharashtra, punjab, karnataka, rajasthan (lines 7–10)
- **Seasons**: kharif, rabi, summer (lines 11–13)
- Input strings **must** be lowercased + stripped before encoding. Mismatch between input case/values and `feature_importance.csv` causes silent prediction errors.

**Critical Conventions**:
1. **Season inference**: `infer_season_from_month(month)` → {kharif: Jun–Oct, rabi: Nov–Mar, summer: Apr–May, whole year: else}. Used by `/api/predict-auto`.
2. **Profit fields are farmer-visible**; N,P,K and temp/humidity are auto-set by season, hidden from UI (non-technical users).
3. **Feature alignment is non-negotiable**: After `get_dummies`, reindex to `FEATURE_COLUMNS` with `fill_value=0`. Changing feature order or names breaks inference silently.
4. **Model path**: `yield_prediction_model.pkl` at repo root. `FARMER_DASHBOARD_BACKEND/models/` exists but is not auto-loaded; update `app.py` if paths change.

**Running & Testing**:
- **Dev**: `python app.py` → Flask debug on `0.0.0.0:5000`.
- **Conda env (Windows)**: `C:\Users\ujju1\.conda\envs\myenv\python.exe app.py`.
- **Test yield endpoint**: Run `test_yield.py` (uses `app.test_client()`).
- **Test forecast API**: `test_all_apis.py` hits `/api/forecast`, `/api/recommend` (requires `FARMER_DASHBOARD_BACKEND` running separately).

**Example Payloads**:
- **`/api/predict`** (manual Season):
  ```json
  {
    "Crop": "soybean", "State": "maharashtra", "Season": "kharif",
    "Area": 5, "Crop_Year": 2025, "Annual_Rainfall": 1200,
    "Fertilizer": 80000, "Pesticide": 1000, "N": 90, "P": 40, "K": 40,
    "temperature": 28, "humidity": 70, "Price_per_kg": 3500, "Total_Cost": 250000
  }
  ```
- **`/api/predict-auto`** (inferred Season from month):
  ```json
  {"Crop": "soybean", "State": "maharashtra", "month": 8, "Area": 5, ...}
  ```

**Modification Checklist**:
- Changing input preprocessing → also update `FARMER_DASHBOARD_BACKEND/config.py` season mappings + test suite.
- Adding crops/states → retrain model, export new `feature_importance.csv` with all one-hot columns, test with `test_yield.py`.
- Profit formula changes → update both `calculate_profit()` in `app.py` and `profit_calculator.py` in backend for consistency.
- New features → reorder `feature_importance.csv` columns to match model's `feature_names_in_`, never assume column order.

**Where to Learn Patterns**:
- **Inference**: `app.py:preprocess_single_row()` (lines ~65–85) and `model.predict()` call (lines ~100+).
- **Form rendering**: HTML_FORM template (lines ~130+) shows farmer-visible fields only.
- **ARIMA fallback**: `forecast_engine.py:forecast_arima()` (lines ~56+) uses trend + seasonality when ARIMA times out.
- **Backend routing**: `FARMER_DASHBOARD_BACKEND/flask_integration.py` registers `/api/predict-profit`, `/api/forecast-arima`, `/api/recommend-crop`.
