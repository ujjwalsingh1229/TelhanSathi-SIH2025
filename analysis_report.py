"""
COMPREHENSIVE ANALYSIS REPORT
Yield Prediction Model + Oilseed Price Forecasting
=====================================================
"""

import pandas as pd
import numpy as np
import joblib
import warnings
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

print("=" * 80)
print("FARMER PROFIT DASHBOARD - COMPLETE ANALYSIS")
print("=" * 80)

# ============================================================================
# PART 1: YIELD PREDICTION MODEL ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: YIELD PREDICTION MODEL")
print("=" * 80)

try:
    model = joblib.load("yield_prediction_model.pkl")
    print("✓ Model loaded successfully")
    
    # Get model info
    n_features = len(model.feature_names_in_) if hasattr(model, 'feature_names_in_') else 106
    print(f"  • Features: {n_features}")
    print(f"  • Model Type: RandomForest Regressor")
    print(f"  • Target: Yield (kg/hectare)")
    
    # Show sample features
    if hasattr(model, 'feature_names_in_'):
        features_sample = list(model.feature_names_in_)[:15]
        print(f"  • Sample Features: {', '.join(features_sample[:5])}... (+{len(model.feature_names_in_)-5} more)")
    
    # Feature importance (if available)
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
        top_indices = np.argsort(importance)[-5:][::-1]
        
        print("\n  Top 5 Most Important Features:")
        if hasattr(model, 'feature_names_in_'):
            for i, idx in enumerate(top_indices, 1):
                fname = model.feature_names_in_[idx]
                fimportance = importance[idx]
                print(f"    {i}. {fname:30s} : {fimportance:.4f}")
        
except Exception as e:
    print(f"✗ Error loading model: {e}")

# Test prediction
print("\n" + "-" * 80)
print("TEST PREDICTION")
print("-" * 80)

try:
    test_input = {
        'Crop': 'soybean',
        'State': 'maharashtra',
        'Area': 5.0,
        'Annual_Rainfall': 1200,
        'Fertilizer': 80000,
        'Pesticide': 1000,
        'N': 90,
        'P': 40,
        'K': 40,
        'temperature': 28,
        'humidity': 70,
        'Crop_Year': 2025,
        'Season': 'kharif'
    }
    
    df_test = pd.DataFrame([test_input])
    categorical_cols = ['Crop', 'State', 'Season']
    df_encoded = pd.get_dummies(df_test, columns=categorical_cols, drop_first=False)
    df_aligned = df_encoded.reindex(columns=model.feature_names_in_, fill_value=0)
    
    prediction_kg = model.predict(df_aligned)[0]
    
    # Convert to farmer-friendly units
    total_yield_kg = prediction_kg * test_input['Area']
    total_yield_quintals = total_yield_kg / 100
    yield_per_acre = (prediction_kg * 0.404686) / 100  # 1 hectare ≈ 2.47 acres
    
    print(f"Input Crop: {test_input['Crop'].upper()}")
    print(f"Input State: {test_input['State'].upper()}")
    print(f"Input Area: {test_input['Area']} hectares")
    print(f"Input Season: {test_input['Season'].upper()}")
    print(f"\nPredicted Yield: {prediction_kg:.2f} kg/hectare")
    print(f"Total Yield: {total_yield_quintals:.2f} quintals")
    print(f"Yield per Acre: {yield_per_acre:.2f} quintals/acre")
    
    # Calculate profit
    price_per_kg = test_input.get('Price_per_kg', 3500) / 100  # Convert to per kg from per quintal
    total_cost = test_input.get('Total_Cost', 250000)
    
    total_revenue = total_yield_kg * price_per_kg
    net_profit = total_revenue - total_cost
    profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    roi = (net_profit / total_cost * 100) if total_cost > 0 else 0
    
    print(f"\n--- Profit Calculation ---")
    print(f"Price per kg: ₹{price_per_kg:.2f}")
    print(f"Total Revenue: ₹{total_revenue:,.2f}")
    print(f"Total Cost: ₹{total_cost:,.2f}")
    print(f"Net Profit: ₹{net_profit:,.2f}")
    print(f"Profit Margin: {profit_margin:.2f}%")
    print(f"ROI: {roi:.2f}%")
    
except Exception as e:
    print(f"✗ Error in test prediction: {e}")


# ============================================================================
# PART 2: OILSEED PRICE FORECASTING (ARIMA)
# ============================================================================
print("\n" + "=" * 80)
print("PART 2: OILSEED PRICE FORECASTING (ARIMA TIME SERIES)")
print("=" * 80)

try:
    # Load data
    df = pd.read_csv("indian_oilseeds_prices.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    
    print(f"\n✓ Data loaded: {len(df)} records")
    print(f"  • Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(f"  • Oilseeds: {', '.join(df['Commodity'].unique())}")
    
    # ARIMA Analysis
    print("\n" + "-" * 80)
    print("ARIMA MODEL PERFORMANCE METRICS")
    print("-" * 80)
    
    results = []
    all_forecasts = []
    
    for commodity, g in df.groupby("Commodity"):
        g = g.set_index("Date").asfreq("MS")
        series = g["Price"]
        
        # Train-test split (last 12 months as test)
        train = series.iloc[:-12]
        test = series.iloc[-12:]
        
        # Find best ARIMA order
        best_aic = np.inf
        best_order = (0, 1, 0)
        
        for p in [0, 1, 2]:
            for d in [0, 1]:
                for q in [0, 1, 2]:
                    try:
                        model_temp = ARIMA(train, order=(p, d, q))
                        res = model_temp.fit()
                        if res.aic < best_aic:
                            best_aic = res.aic
                            best_order = (p, d, q)
                    except:
                        continue
        
        # Fit on train for evaluation
        eval_model = ARIMA(train, order=best_order).fit()
        preds = eval_model.forecast(steps=12)
        
        mae = mean_absolute_error(test, preds)
        rmse = np.sqrt(mean_squared_error(test, preds))
        mape = np.mean(np.abs((test - preds) / test)) * 100
        
        results.append({
            "Commodity": commodity,
            "Best_Order": best_order,
            "AIC": best_aic,
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape,
            "Mean_Price": series.mean()
        })
        
        # Fit on full data for future forecast
        final_model = ARIMA(series, order=best_order).fit()
        future_index = pd.date_range(series.index[-1] + pd.offsets.MonthBegin(1),
                                    periods=12, freq="MS")
        future_forecast = final_model.forecast(steps=12)
        
        tmp = pd.DataFrame({
            "Commodity": commodity,
            "Date": future_index,
            "Forecast_Price": future_forecast.values
        })
        all_forecasts.append(tmp)
    
    metrics_df = pd.DataFrame(results)
    forecast_df = pd.concat(all_forecasts, ignore_index=True)
    
    print("\n" + metrics_df.to_string(index=False))
    
    # Summary
    print("\n" + "-" * 80)
    print("FORECAST SUMMARY")
    print("-" * 80)
    print(f"\nBest ARIMA Model (Lowest RMSE): {metrics_df.loc[metrics_df['RMSE'].idxmin(), 'Commodity']}")
    print(f"  • ARIMA Order: {metrics_df.loc[metrics_df['RMSE'].idxmin(), 'Best_Order']}")
    print(f"  • RMSE: ₹{metrics_df['RMSE'].min():.2f}")
    print(f"  • MAE: ₹{metrics_df.loc[metrics_df['RMSE'].idxmin(), 'MAE']:.2f}")
    
    # 12-month forecast
    print("\n" + "-" * 80)
    print("12-MONTH PRICE FORECASTS")
    print("-" * 80)
    
    for commodity in metrics_df['Commodity'].unique():
        forecast_subset = forecast_df[forecast_df['Commodity'] == commodity]
        avg_forecast = forecast_subset['Forecast_Price'].mean()
        min_forecast = forecast_subset['Forecast_Price'].min()
        max_forecast = forecast_subset['Forecast_Price'].max()
        
        print(f"\n{commodity}:")
        print(f"  • Average Forecast (12M): ₹{avg_forecast:.2f}/quintal")
        print(f"  • Min: ₹{min_forecast:.2f}")
        print(f"  • Max: ₹{max_forecast:.2f}")
        print(f"  • First Month: ₹{forecast_subset.iloc[0]['Forecast_Price']:.2f}")
    
    # Save forecasts
    forecast_df.to_csv("oilseed_forecasts_12month.csv", index=False)
    print(f"\n✓ Forecasts saved to: oilseed_forecasts_12month.csv")
    
except FileNotFoundError as e:
    print(f"✗ Data file not found: {e}")
except Exception as e:
    print(f"✗ Error in forecasting: {e}")


# ============================================================================
# PART 3: PROFIT ANALYSIS FOR OILSEEDS
# ============================================================================
print("\n" + "=" * 80)
print("PART 3: OILSEED PROFITABILITY ANALYSIS")
print("=" * 80)

try:
    print("\n" + "-" * 80)
    print("PROFIT SCENARIOS (2-hectare farm, ₹25,000/hectare cost)")
    print("-" * 80)
    
    area_hectares = 2
    cost_per_hectare = 25000
    total_cost = area_hectares * cost_per_hectare
    
    # Average yields for oilseeds (quintal/hectare)
    yields = {
        'Soybean': 20,
        'Mustard': 15,
        'Groundnut': 18,
        'Sunflower': 16,
        'Sesame': 12
    }
    
    profit_analysis = []
    
    for commodity in metrics_df['Commodity'].unique():
        if commodity in yields:
            yield_q = yields[commodity]
            yield_kg = yield_q * 100
            total_yield = yield_kg * area_hectares
            
            # Get forecast price
            forecast_price = forecast_df[forecast_df['Commodity'] == commodity]['Forecast_Price'].mean()
            
            total_revenue = total_yield * (forecast_price / 100)  # Convert to kg
            net_profit = total_revenue - total_cost
            profit_per_hectare = net_profit / area_hectares
            roi = (net_profit / total_cost) * 100
            
            profit_analysis.append({
                'Commodity': commodity,
                'Yield (Q/Ha)': yield_q,
                'Forecast Price': f"₹{forecast_price:.0f}",
                'Total Revenue': f"₹{total_revenue:,.0f}",
                'Total Cost': f"₹{total_cost:,.0f}",
                'Net Profit': f"₹{net_profit:,.0f}",
                'ROI %': f"{roi:.1f}%"
            })
    
    profit_df = pd.DataFrame(profit_analysis)
    print("\n" + profit_df.to_string(index=False))
    
    print("\n✓ Best ROI: Check Net Profit column for highest returns")
    
except Exception as e:
    print(f"✗ Error in profit analysis: {e}")


print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print("\nFiles generated:")
print("  • oilseed_forecasts_12month.csv - 12-month price forecasts")
print("\nNext Steps:")
print("  1. Use yield predictions for crop planning")
print("  2. Check oilseed forecasts to optimize crop selection")
print("  3. Calculate profitability for your specific farm conditions")
print("\n")
