"""
Farmer Profit Comparison Dashboard - Flask Application

Main entry point for the backend server.
Starts a Flask development server with all dashboard endpoints.

Usage:
    python app.py
    
Then access:
    - http://localhost:5000/api/predict-profit (POST)
    - http://localhost:5000/api/forecast-arima (POST)
    - http://localhost:5000/api/recommend-crop (POST)
"""

import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from flask_integration import register_dashboard_routes
import logging
from config import LOGGING_CONFIG

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Register dashboard routes
register_dashboard_routes(app)


@app.route('/', methods=['GET'])
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'Farmer Profit Comparison Dashboard',
        'version': '1.0.0',
        'endpoints': {
            'predict_profit': 'POST /api/predict-profit',
            'forecast_arima': 'POST /api/forecast-arima',
            'recommend_crop': 'POST /api/recommend-crop'
        }
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'Check documentation for available endpoints: /api/predict-profit, /api/forecast-arima, /api/recommend-crop'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'Please check the server logs for details'
    }), 500


if __name__ == '__main__':
    print("""
    ========================================
    Farmer Profit Comparison Dashboard
    ========================================
    
    Starting Flask server...
    
    Available Endpoints:
    - POST http://localhost:5000/api/predict-profit
    - POST http://localhost:5000/api/forecast-arima
    - POST http://localhost:5000/api/recommend-crop
    
    Health Check:
    - GET http://localhost:5000/
    - GET http://localhost:5000/health
    
    Test with:
    curl -X POST http://localhost:5000/api/predict-profit \\
      -H "Content-Type: application/json" \\
      -d '{"oilseed_name": "Soybean", "oilseed_area": 2, ...}'
    
    ========================================
    """)
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
