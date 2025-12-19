# 🌾 Farmer Profit Comparison Dashboard
## User-Friendly Interactive Tool for Crop Selection with ARIMA Forecasting

---

## 📋 Overview

The **Farmer Profit Comparison Dashboard** is an interactive Jupyter notebook that empowers farmers to make data-driven decisions by comparing profitability between **oil seeds** and **traditional crops**. It features:

✅ **User-Input Interface** - Farmers can enter their specific crop parameters  
✅ **Real-Time Profit Calculation** - Instant revenue, cost, and profit metrics  
✅ **ARIMA Price Forecasting** - 12-month profit predictions with confidence intervals  
✅ **Cultivation Ease Analysis** - Difficulty scoring for different crops  
✅ **Automated Recommendation Engine** - Smart crop selection based on multiple factors  
✅ **Interactive Visualizations** - Beautiful charts and radar diagrams  

---

## 🚀 Key Features

### 1. **User Input Customization**
Farmers can modify:
- Crop names (Soybean, Groundnut, Mustard, Maize, Wheat, Rice, Cotton, etc.)
- Land area (in hectares)
- Cost breakdown (initial investment, maintenance, harvest)
- Expected yield (kg/hectare)
- Market price (₹/kg)

### 2. **Comprehensive Profit Metrics**
Calculates:
- **Total Revenue** = Yield × Price
- **Total Cost** = (Initial + Maintenance + Harvest) × Land Area
- **Net Profit** = Revenue - Cost
- **Profit Margin** = (Profit / Revenue) × 100%
- **ROI** = (Profit / Cost) × 100%
- **Profit per kg** = Net Profit / Total Yield

### 3. **ARIMA-Based Forecasting**
- Generates 24 months of historical profit data with seasonal variations
- Trains ARIMA(1,1,1) models for both crops
- Predicts 12-month profit trends with **95% confidence intervals**
- Shows profit stability and variability patterns

### 4. **Visualization Suite**

#### Static Charts (Matplotlib):
- Net profit comparison
- ROI comparison
- Profit margin comparison
- Revenue vs Cost analysis
- Historical + forecasted profit trends with confidence bands

#### Interactive Charts (Plotly):
- Individual 12-month profit forecasts with hover details
- Side-by-side forecast comparison
- Radar chart for comprehensive performance metrics
- Shaded confidence intervals for forecast uncertainty

### 5. **Smart Recommendation Engine**
Scores crops on:
1. **Net Profit** (weight: 30%) - Absolute earnings potential
2. **ROI** (weight: 25%) - Return on investment percentage
3. **Profit Margin** (weight: 20%) - Profitability as % of revenue
4. **Cultivation Ease** (weight: 15%) - Difficulty scale (1-10)
5. **Forecast Stability** (weight: 10%) - Consistency of predictions

**Final Score: 0-10 points** - Automated recommendation with reasoning

---

## 📊 Example Output

### Case: Soybean vs Maize

**Metrics Comparison:**
```
Soybean (2 hectares):
  • Total Yield: 4,000 kg
  • Total Revenue: ₹240,000
  • Total Cost: ₹90,000
  • NET PROFIT: ₹150,000
  • Profit Margin: 62.5%
  • ROI: 166.67%

Maize (2 hectares):
  • Total Yield: 10,000 kg
  • Total Revenue: ₹250,000
  • Total Cost: ₹72,000
  • NET PROFIT: ₹178,000
  • Profit Margin: 71.2%
  • ROI: 247.22%
```

**Recommendation:**
```
✅ MAIZE IS RECOMMENDED (Score: 10/10 vs Soybean: 0/10)

Benefits:
  • 18.7% higher net profit (₹28,000 more)
  • Better ROI: 247.2% vs 166.7%
  • Higher profit margin: 71.2% vs 62.5%
  • Easier cultivation (difficulty 3/10 vs 4/10)
  • More stable profit forecast
```

**12-Month Forecast:**
- Maize: Average ₹157,545/month (range: ₹29k - ₹286k)
- Soybean: Average ₹105,115/month (range: ₹8k - ₹215k)

---

## 🔧 How to Use

### Step 1: Modify Input Parameters (Section 2 & 3)
```python
# Oil seed parameters
oilseed_name = "Soybean"
oilseed_land_area = 2.0  # hectares
oilseed_expected_yield = 2000  # kg/hectare
oilseed_market_price = 60  # ₹/kg
oilseed_initial_investment = 15000  # ₹/hectare
oilseed_maintenance_cost = 25000  # ₹/hectare

# Crop parameters (similar structure)
crop_name = "Maize"
crop_land_area = 2.0
crop_expected_yield = 5000
crop_market_price = 25
# ... etc
```

### Step 2: Run All Cells in Order
Execute cells sequentially:
1. **Import Libraries** (Section 1)
2. **Set Oil Seed Inputs** (Section 2)
3. **Set Crop Inputs** (Section 3)
4. **Calculate Metrics** (Section 4)
5. **Compare Profitability** (Section 5)
6. **View Profit Comparisons** charts
7. **Generate Historical Data & ARIMA Models** (Section 6)
8. **View Profit Forecasts** (Section 7)
9. **Get Recommendation** (Section 8)

### Step 3: Interpret Results
- Compare profit metrics in tables
- Study visualization trends and patterns
- Read automated recommendation with scoring breakdown
- Check 12-month forecast for risk assessment

---

## 📈 Cultivation Factors Database

The dashboard includes cultivation difficulty assessments for common crops:

| Crop | Difficulty | Water | Labor | Pests | Market |
|------|-----------|-------|-------|-------|--------|
| **Soybean** | 4/10 | Moderate | Low-Mod | Moderate | High |
| **Groundnut** | 5/10 | Low | Moderate | High | High |
| **Mustard** | 3/10 | Low | Low | Low | High |
| **Sunflower** | 4/10 | Moderate | Low | Moderate | High |
| **Maize** | 3/10 | High | Moderate | High | High |
| **Wheat** | 2/10 | Low | Low | Low | High |
| **Rice** | 6/10 | Very High | High | High | High |
| **Cotton** | 7/10 | High | High | Very High | High |

---

## 🎯 Farmer Decision Guide

### **4-Step Workflow:**

1. **Know Your State's Top Choice**
   - Check "Recommended Oilseed by State" from IoT system
   - See which crop dominates your region

2. **Check If It's Stable**
   - Green (CV < 15%): Safe bet, grow anywhere
   - Yellow (CV 15-30%): Good, monitor conditions
   - Red (CV > 30%): Risky, optimize before planting

3. **Consider Your Conditions**
   - Input your soil nutrients (N, P, K)
   - Enter IoT sensor readings
   - See crop suitability scores

4. **Explore Profit Scenarios**
   - Run profit simulator
   - Try "what if" scenarios
   - Compare baseline vs improved inputs
   - Make investment decision

---

## 💡 Key Insights

### Why Oil Seeds Can Be Better:
✅ **Higher profit per kg** (typically ₹30-60/kg vs ₹10-30/kg for grains)  
✅ **Lower input costs** (less water, fewer pesticides)  
✅ **Easier cultivation** (simpler pest management)  
✅ **Better market access** (consistent buyer demand)  
✅ **Resilient to climate** (drought-tolerant varieties available)

### Why Traditional Crops Can Be Better:
✅ **Higher absolute yield** (greater total production)  
✅ **Lower cultivation difficulty** (more familiar practices)  
✅ **Established infrastructure** (better supply chains)  
✅ **Lower investment risk** (proven performance)  
✅ **Easier labor sourcing** (more skilled workers available)

---

## 🔍 ARIMA Forecasting Methodology

The dashboard uses **ARIMA(1,1,1)** models for time series forecasting:

- **Data**: 24 months of historical profit data with seasonal patterns
- **Model**: Auto-Regressive Integrated Moving Average (1,1,1)
- **Forecast**: 12 months ahead with 95% confidence intervals
- **Interpretation**:
  - Solid line = Most likely profit trajectory
  - Shaded area = Range of expected outcomes (95% confidence)
  - Wider bands = More uncertain forecasts
  - Narrower bands = More stable predictions

---

## 🛠️ Customization Options

### Add New Crops:
```python
cultivation_factors['YourCrop'] = {
    'difficulty': 3,  # 1-10 scale
    'water_requirement': 'Low',
    'labor': 'Low',
    'pests': 'Low',
    'market_access': 'High'
}
```

### Modify Cost Structure:
Update the cost components in Section 2 & 3 for your region:
```python
oilseed_initial_investment = 15000  # Your local seed/tool cost
oilseed_maintenance_cost = 25000   # Your labor + fertilizer cost
oilseed_harvest_cost = 5000        # Your harvesting expense
```

### Adjust Time Horizons:
Change forecast periods from 12 to 24 months:
```python
forecast_periods = 24  # From 12 to 24 months
```

---

## 📊 File Structure

```
Farmer_Profit_Comparison_Dashboard.ipynb
├── Section 1: Import Libraries
├── Section 2: Oil Seed Inputs
├── Section 3: Crop Inputs
├── Section 4: Profit Metrics Calculation
├── Section 5: Profitability Comparison & Visualizations
├── Section 6: ARIMA Model Training
├── Section 7: 12-Month Forecasts with Visualizations
├── Section 8: Recommendation Engine & Radar Chart
└── Usage Instructions & Decision Guide
```

**File Size**: ~411 KB  
**Runtime**: ~5-10 seconds (first run with ARIMA training)  
**Dependencies**: pandas, numpy, matplotlib, seaborn, plotly, statsmodels

---

## ✅ System Requirements

- Python 3.7+
- Jupyter Notebook or JupyterLab
- Libraries:
  - `pandas` (data manipulation)
  - `numpy` (numerical computing)
  - `matplotlib` (static plots)
  - `seaborn` (statistical visualizations)
  - `plotly` (interactive charts)
  - `statsmodels` (ARIMA forecasting)

---

## 🚀 Quick Start

1. **Open notebook** in Jupyter
2. **Run all cells** (Kernel → Restart & Run All)
3. **Modify input values** in Sections 2-3 with your data
4. **Re-run calculation cells** (4, 5, 6, 7, 8)
5. **Review recommendations** in Section 8
6. **Make farming decision** based on analysis

---

## 📞 Support & Tips

### If Forecast Looks Unrealistic:
- Check that historical data was generated correctly
- Verify ARIMA models trained successfully (look for "AIC" values)
- Consider extending historical period from 24 to 36 months

### If Recommendation Seems Wrong:
- Review the scoring breakdown in Section 8
- Check if cultivation ease factors are accurate for your region
- Verify market prices match your local rates

### For Better Results:
- Use actual historical price data instead of generated data
- Update costs based on your specific region/farm
- Include actual seasonal variation patterns
- Integrate real IoT sensor data from Section 7

---

## 📝 Version History

**v1.0** (Dec 2025)
- Initial release
- 8 comprehensive sections
- ARIMA forecasting with confidence intervals
- Interactive Plotly visualizations
- Automated recommendation engine
- Cultivation difficulty assessment

---

**Created for**: SIH 2024 - Smart India Hackathon  
**Purpose**: Empower farmers with AI-driven decision support  
**Maintenance**: Open for enhancements and customization  

---

## 🌍 Impact Goals

- Help 1000+ farmers make informed crop choices
- Increase average profitability by 20-30%
- Reduce cultivation risks through forecasting
- Bridge gap between traditional and modern farming
- Promote sustainable oilseed cultivation

