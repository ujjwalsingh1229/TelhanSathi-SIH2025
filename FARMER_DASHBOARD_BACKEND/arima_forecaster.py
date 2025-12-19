import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

def train_arima_model(historical_data, order=(1, 1, 1)):
    """
    Train ARIMA model on historical profit data
    
    Args:
        historical_data (list or np.array): 24 months of historical profits
        order (tuple): ARIMA(p,d,q) parameters
    
    Returns:
        ARIMA fitted model object
    """
    try:
        if len(historical_data) < 12:
            raise ValueError("Need at least 12 months of historical data")
        
        model = ARIMA(historical_data, order=order)
        fitted_model = model.fit()
        return fitted_model
    except Exception as e:
        raise ValueError(f"Error training ARIMA model: {str(e)}")


def forecast_profits(fitted_model, periods=12):
    """
    Generate profit forecasts with confidence intervals
    
    Args:
        fitted_model: Trained ARIMA model
        periods (int): Number of months to forecast
    
    Returns:
        dict: Forecast mean and confidence intervals
    """
    try:
        forecast = fitted_model.get_forecast(steps=periods)
        forecast_mean = forecast.predicted_mean
        forecast_ci = forecast.conf_int(alpha=0.05)  # 95% CI
        
        # Handle both Series and array returns
        forecast_mean_values = forecast_mean.values if hasattr(forecast_mean, 'values') else forecast_mean
        ci_lower = forecast_ci.iloc[:, 0].values if hasattr(forecast_ci, 'iloc') else forecast_ci[:, 0]
        ci_upper = forecast_ci.iloc[:, 1].values if hasattr(forecast_ci, 'iloc') else forecast_ci[:, 1]
        
        forecast_data = []
        for i, (mean, lower, upper) in enumerate(zip(forecast_mean_values, ci_lower, ci_upper)):
            forecast_data.append({
                'period': i + 1,
                'predicted_profit': round(float(mean), 0),
                'confidence_lower': round(float(lower), 0),
                'confidence_upper': round(float(upper), 0)
            })
        
        return {
            'forecast': forecast_data,
            'average_forecast': round(float(np.mean(forecast_mean_values)), 0),
            'forecast_std': round(float(np.std(forecast_mean_values)), 0),
            'aic': round(fitted_model.aic, 2)
        }
    except Exception as e:
        raise ValueError(f"Error generating forecasts: {str(e)}")


def generate_seasonal_historical_data(base_profit, months=24, season='regular'):
    """
    Generate realistic historical profit data with seasonal patterns
    
    Args:
        base_profit (float): Base profit amount
        months (int): Number of months to generate
        season (str): 'regular' or 'oilseed' for different patterns
    
    Returns:
        np.array: Generated historical profit data
    """
    np.random.seed(42)
    
    if season == 'oilseed':
        # Oil seed seasonal pattern (higher in Oct-Nov-Dec harvest)
        seasonal_pattern = np.sin(np.arange(months) * 2 * np.pi / 12) * 0.3 + 1
    else:
        # Traditional crop pattern (higher in Jun-Jul-Aug)
        seasonal_pattern = np.sin((np.arange(months) - 3) * 2 * np.pi / 12) * 0.25 + 1
    
    noise = np.random.normal(0, base_profit * 0.1, months)
    historical_profit = base_profit * seasonal_pattern + noise
    
    return np.maximum(historical_profit, 0)  # Ensure no negative values


def get_forecast_confidence_summary(forecast_data):
    """
    Generate summary statistics from forecast
    
    Args:
        forecast_data (list): Forecast data from forecast_profits()
    
    Returns:
        dict: Summary statistics
    """
    try:
        forecasts = [f['predicted_profit'] for f in forecast_data]
        lowers = [f['confidence_lower'] for f in forecast_data]
        uppers = [f['confidence_upper'] for f in forecast_data]
        
        return {
            'mean_forecast': np.mean(forecasts),
            'min_forecast': min(forecasts),
            'max_forecast': max(forecasts),
            'std_forecast': np.std(forecasts),
            'avg_ci_width': np.mean([u - l for u, l in zip(uppers, lowers)]),
            'risk_level': 'HIGH' if np.std(forecasts) > np.mean(forecasts) * 0.3 else 'MODERATE' if np.std(forecasts) > np.mean(forecasts) * 0.15 else 'LOW'
        }
    except Exception as e:
        raise ValueError(f"Error calculating forecast summary: {str(e)}")


def compare_forecast_stability(forecast_data_1, forecast_data_2):
    """
    Compare stability of two forecasts
    
    Args:
        forecast_data_1 (list): First forecast data
        forecast_data_2 (list): Second forecast data
    
    Returns:
        dict: Comparison results
    """
    try:
        std_1 = np.std([f['predicted_profit'] for f in forecast_data_1])
        std_2 = np.std([f['predicted_profit'] for f in forecast_data_2])
        
        return {
            'forecast_1_std': std_1,
            'forecast_2_std': std_2,
            'more_stable': 1 if std_1 < std_2 else 2,
            'stability_ratio': std_2 / std_1 if std_1 > 0 else 0
        }
    except Exception as e:
        raise ValueError(f"Error comparing forecasts: {str(e)}")
