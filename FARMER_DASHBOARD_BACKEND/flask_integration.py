"""
Flask Integration Module for Farmer Profit Comparison Dashboard

Provides 3 main API endpoints:
1. /api/predict-profit - Calculate profit metrics for oilseed vs alternative crop
2. /api/forecast-arima - Generate 12-month profit forecast with confidence intervals
3. /api/recommend-crop - Get recommendation with 5-factor scoring

Usage in Flask app:
    from flask import Flask
    from flask_integration import register_dashboard_routes
    
    app = Flask(__name__)
    register_dashboard_routes(app)
"""

from flask import Blueprint, request, jsonify
import numpy as np
import logging
from profit_calculator import calculate_profit_metrics, compare_crops, validate_crop_input
from arima_forecaster import train_arima_model, forecast_profits, generate_seasonal_historical_data
from recommendation_engine import (
    generate_recommendation,
    get_cultivation_ease,
    format_recommendation_output,
    calculate_recommendation_score_breakdown
)

logger = logging.getLogger(__name__)


# Create Blueprint
dashboard_bp = Blueprint('farmer_dashboard', __name__, url_prefix='/api')


@dashboard_bp.route('/predict-profit', methods=['POST'])
def predict_profit():
    """
    Calculate profit metrics for oil seed and alternative crop
    
    Request JSON:
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
    
    Returns:
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
        "crop": {...},
        "comparison": {
            "more_profitable": "Maize",
            "profit_difference": 28000,
            "roi_difference": 80.55,
            "percentage_better": "18.65%"
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        oilseed_data = {
            'name': data.get('oilseed_name', 'Soybean'),
            'land_area': float(data.get('oilseed_area', 2)),
            'expected_yield': float(data.get('oilseed_yield', 2000)),
            'market_price': float(data.get('oilseed_price', 60)),
            'total_cost_per_hectare': float(data.get('oilseed_cost', 45000))
        }
        
        crop_data = {
            'name': data.get('crop_name', 'Maize'),
            'land_area': float(data.get('crop_area', 2)),
            'expected_yield': float(data.get('crop_yield', 5000)),
            'market_price': float(data.get('crop_price', 25)),
            'total_cost_per_hectare': float(data.get('crop_cost', 36000))
        }
        
        # Validate inputs
        is_valid_os, error_os = validate_crop_input(oilseed_data)
        is_valid_cp, error_cp = validate_crop_input(crop_data)
        
        if not is_valid_os or not is_valid_cp:
            return jsonify({
                'success': False,
                'error': f"Oilseed: {error_os}" if error_os else f"Crop: {error_cp}"
            }), 400
        
        # Calculate metrics
        oilseed_metrics = calculate_profit_metrics(oilseed_data)
        crop_metrics = calculate_profit_metrics(crop_data)
        comparison = compare_crops(oilseed_metrics, crop_metrics)
        
        return jsonify({
            'success': True,
            'oilseed': {
                'name': oilseed_data['name'],
                'total_yield': oilseed_metrics['total_yield'],
                'total_revenue': oilseed_metrics['total_revenue'],
                'total_cost': oilseed_metrics['total_cost'],
                'net_profit': oilseed_metrics['net_profit'],
                'profit_margin': round(oilseed_metrics['profit_margin'], 2),
                'roi': round(oilseed_metrics['roi'], 2),
                'profit_per_kg': round(oilseed_metrics['profit_per_kg'], 2)
            },
            'crop': {
                'name': crop_data['name'],
                'total_yield': crop_metrics['total_yield'],
                'total_revenue': crop_metrics['total_revenue'],
                'total_cost': crop_metrics['total_cost'],
                'net_profit': crop_metrics['net_profit'],
                'profit_margin': round(crop_metrics['profit_margin'], 2),
                'roi': round(crop_metrics['roi'], 2),
                'profit_per_kg': round(crop_metrics['profit_per_kg'], 2)
            },
            'comparison': comparison
        }), 200
    
    except ValueError as e:
        return jsonify({'success': False, 'error': f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/forecast-arima', methods=['POST'])
def forecast_arima():
    """
    Generate 12-month ARIMA forecast for profit predictions
    
    Request JSON:
    {
        "oilseed_name": "Soybean",
        "oilseed_base_profit": 150000,
        "crop_name": "Maize",
        "crop_base_profit": 178000,
        "forecast_months": 12,
        "arima_order": [1, 1, 1]
    }
    
    Returns:
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
                },
                ...
            ],
            "average_12month": 105115,
            "forecast_std": 35000,
            "aic": 532.64
        },
        "crop_forecast": {...},
        "comparison": {
            "more_stable": "Maize",
            "stability_ratio": 1.15
        }
    }
    """
    try:
        data = request.get_json()
        
        oilseed_name = data.get('oilseed_name', 'Soybean')
        crop_name = data.get('crop_name', 'Maize')
        oilseed_base = float(data.get('oilseed_base_profit', 150000))
        crop_base = float(data.get('crop_base_profit', 178000))
        forecast_months = int(data.get('forecast_months', 12))
        arima_order = tuple(data.get('arima_order', [1, 1, 1]))
        
        # Generate seasonal historical data (24 months)
        oilseed_history = generate_seasonal_historical_data(oilseed_base, months=24, season='kharif')
        crop_history = generate_seasonal_historical_data(crop_base, months=24, season='summer')
        
        # Train ARIMA models
        os_model = train_arima_model(oilseed_history, order=arima_order)
        cp_model = train_arima_model(crop_history, order=arima_order)
        
        # Generate forecasts
        os_forecast = forecast_profits(os_model, periods=forecast_months)
        cp_forecast = forecast_profits(cp_model, periods=forecast_months)
        
        # Extract forecast values for stability comparison
        os_forecast_values = np.array([f['predicted_profit'] for f in os_forecast['forecast']])
        cp_forecast_values = np.array([f['predicted_profit'] for f in cp_forecast['forecast']])
        
        os_stability = np.std(os_forecast_values)
        cp_stability = np.std(cp_forecast_values)
        more_stable = 'oilseed' if os_stability < cp_stability else 'crop'
        stability_ratio = max(os_stability, cp_stability) / min(os_stability, cp_stability)
        
        return jsonify({
            'success': True,
            'oilseed_forecast': {
                'name': oilseed_name,
                'forecast': os_forecast['forecast'],
                'average_12month': os_forecast['average_forecast'],
                'forecast_std': os_forecast['forecast_std'],
                'aic': round(os_model.aic, 2)
            },
            'crop_forecast': {
                'name': crop_name,
                'forecast': cp_forecast['forecast'],
                'average_12month': cp_forecast['average_forecast'],
                'forecast_std': cp_forecast['forecast_std'],
                'aic': round(cp_model.aic, 2)
            },
            'comparison': {
                'more_stable': more_stable,
                'stability_ratio': round(stability_ratio, 2)
            }
        }), 200
    
    except ValueError as e:
        return jsonify({'success': False, 'error': f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@dashboard_bp.route('/recommend-crop', methods=['POST'])
def recommend_crop():
    """
    Generate crop recommendation with 5-factor scoring
    
    Combines profit metrics, ROI, margins, cultivation ease, and forecast stability
    
    Request JSON:
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
    
    Returns:
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
        "score_breakdown": {...}
    }
    """
    try:
        data = request.get_json()
        
        # Prepare crop data
        oilseed_data = {
            'name': data.get('oilseed_name', 'Soybean'),
            'land_area': float(data.get('oilseed_area', 2)),
            'expected_yield': float(data.get('oilseed_yield', 2000)),
            'market_price': float(data.get('oilseed_price', 60)),
            'total_cost_per_hectare': float(data.get('oilseed_cost', 45000))
        }
        
        crop_data = {
            'name': data.get('crop_name', 'Maize'),
            'land_area': float(data.get('crop_area', 2)),
            'expected_yield': float(data.get('crop_yield', 5000)),
            'market_price': float(data.get('crop_price', 25)),
            'total_cost_per_hectare': float(data.get('crop_cost', 36000))
        }
        
        # Validate inputs
        is_valid_os, error_os = validate_crop_input(oilseed_data)
        is_valid_cp, error_cp = validate_crop_input(crop_data)
        
        if not is_valid_os or not is_valid_cp:
            return jsonify({
                'success': False,
                'error': f"Oilseed: {error_os}" if error_os else f"Crop: {error_cp}"
            }), 400
        
        # Calculate metrics
        oilseed_metrics = calculate_profit_metrics(oilseed_data)
        crop_metrics = calculate_profit_metrics(crop_data)
        
        # Get cultivation factors
        oilseed_ease = get_cultivation_ease(oilseed_data['name'])
        crop_ease = get_cultivation_ease(crop_data['name'])
        
        # Generate forecasts
        oilseed_history = generate_seasonal_historical_data(oilseed_metrics['net_profit'], months=24, season='kharif')
        crop_history = generate_seasonal_historical_data(crop_metrics['net_profit'], months=24, season='summer')
        
        os_model = train_arima_model(oilseed_history, order=(1, 1, 1))
        cp_model = train_arima_model(crop_history, order=(1, 1, 1))
        
        os_forecast = forecast_profits(os_model, periods=12)
        cp_forecast = forecast_profits(cp_model, periods=12)
        
        os_forecast_values = np.array([f['predicted_profit'] for f in os_forecast['forecast']])
        cp_forecast_values = np.array([f['predicted_profit'] for f in cp_forecast['forecast']])
        
        # Generate recommendation
        score_os, score_cp, reasons_os, reasons_cp = generate_recommendation(
            oilseed_metrics, crop_metrics, oilseed_data, crop_data,
            oilseed_ease, crop_ease, os_forecast_values, cp_forecast_values
        )
        
        # Format output
        recommendation = format_recommendation_output(
            score_os, score_cp, reasons_os, reasons_cp,
            oilseed_data, crop_data,
            oilseed_metrics, crop_metrics,
            oilseed_ease, crop_ease,
            os_forecast_values, cp_forecast_values
        )
        
        # Get score breakdown
        breakdown = calculate_recommendation_score_breakdown(
            oilseed_metrics, crop_metrics,
            oilseed_ease, crop_ease,
            os_forecast_values, cp_forecast_values
        )
        
        return jsonify({
            'success': True,
            'recommendation': recommendation['recommended_crop'],
            'recommendation_score': recommendation['recommendation_score'],
            'alternative_score': recommendation['alternative_score'],
            'score_margin': recommendation['score_margin'],
            'benefits': recommendation['benefits'],
            'estimated_12month_avg': recommendation['estimated_12month_avg'],
            'reasoning': recommendation['reasoning'],
            'score_breakdown': breakdown
        }), 200
    
    except ValueError as e:
        return jsonify({'success': False, 'error': f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def register_dashboard_routes(app):
    """
    Register all dashboard routes to Flask app
    
    Args:
        app: Flask application instance
    
    Usage:
        from flask import Flask
        from flask_integration import register_dashboard_routes
        
        app = Flask(__name__)
        register_dashboard_routes(app)
        app.run(debug=True)
    """
    app.register_blueprint(dashboard_bp)
    return app
