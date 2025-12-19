"""
Unit Tests and API Endpoint Tests for Farmer Dashboard Backend

Test coverage:
- Profit calculation endpoints
- ARIMA forecasting endpoints
- Crop recommendation endpoints
- Input validation
- Error handling

To run:
    python -m pytest test_endpoints.py -v
    python -m pytest test_endpoints.py --cov=. (with coverage)
"""

import unittest
import json
import numpy as np
from flask import Flask
from flask_integration import register_dashboard_routes
from profit_calculator import calculate_profit_metrics, compare_crops, validate_crop_input
from arima_forecaster import train_arima_model, forecast_profits, generate_seasonal_historical_data
from recommendation_engine import generate_recommendation, get_cultivation_ease
from utils import (
    format_currency, format_percentage, sanitize_string,
    calculate_percentage_change, get_risk_level
)


class TestProfitCalculator(unittest.TestCase):
    """Test profit calculation functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.soybean_data = {
            'name': 'Soybean',
            'land_area': 2,
            'expected_yield': 2000,
            'market_price': 60,
            'total_cost_per_hectare': 45000
        }
        
        self.maize_data = {
            'name': 'Maize',
            'land_area': 2,
            'expected_yield': 5000,
            'market_price': 25,
            'total_cost_per_hectare': 36000
        }
    
    def test_calculate_profit_metrics_soybean(self):
        """Test profit calculation for soybean"""
        metrics = calculate_profit_metrics(self.soybean_data)
        
        # Expected: 2 ha * 2000 kg/ha * 60 ₹/kg = 240,000 revenue
        # Expected: 2 ha * 45,000 ₹ = 90,000 cost
        # Expected: 240,000 - 90,000 = 150,000 profit
        
        self.assertEqual(metrics['total_yield'], 4000)
        self.assertEqual(metrics['total_revenue'], 240000)
        self.assertEqual(metrics['total_cost'], 90000)
        self.assertEqual(metrics['net_profit'], 150000)
        self.assertAlmostEqual(metrics['profit_margin'], 62.5, places=1)
        self.assertAlmostEqual(metrics['roi'], 166.67, places=1)
    
    def test_calculate_profit_metrics_maize(self):
        """Test profit calculation for maize"""
        metrics = calculate_profit_metrics(self.maize_data)
        
        # Expected: 2 ha * 5000 kg/ha * 25 ₹/kg = 250,000 revenue
        # Expected: 2 ha * 36,000 ₹ = 72,000 cost
        # Expected: 250,000 - 72,000 = 178,000 profit
        
        self.assertEqual(metrics['total_yield'], 10000)
        self.assertEqual(metrics['total_revenue'], 250000)
        self.assertEqual(metrics['total_cost'], 72000)
        self.assertEqual(metrics['net_profit'], 178000)
        self.assertAlmostEqual(metrics['profit_margin'], 71.2, places=1)
        self.assertAlmostEqual(metrics['roi'], 247.22, places=1)
    
    def test_compare_crops(self):
        """Test crop comparison"""
        soybean_metrics = calculate_profit_metrics(self.soybean_data)
        maize_metrics = calculate_profit_metrics(self.maize_data)
        
        comparison = compare_crops(soybean_metrics, maize_metrics)
        
        self.assertEqual(comparison['more_profitable'], 'second')
        self.assertEqual(comparison['profit_difference'], 28000)
        self.assertIn('percentage_better', comparison)
    
    def test_validate_crop_input_valid(self):
        """Test input validation for valid input"""
        is_valid, error = validate_crop_input(self.soybean_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_crop_input_missing_field(self):
        """Test input validation for missing field"""
        invalid_data = self.soybean_data.copy()
        del invalid_data['land_area']
        
        is_valid, error = validate_crop_input(invalid_data)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_validate_crop_input_negative_value(self):
        """Test input validation for negative values"""
        invalid_data = self.soybean_data.copy()
        invalid_data['land_area'] = -1
        
        is_valid, error = validate_crop_input(invalid_data)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_zero_yield_edge_case(self):
        """Test calculation with zero yield"""
        zero_yield_data = self.soybean_data.copy()
        zero_yield_data['expected_yield'] = 0
        
        metrics = calculate_profit_metrics(zero_yield_data)
        self.assertEqual(metrics['net_profit'], -90000)  # Loss = -cost


class TestArimaForecasting(unittest.TestCase):
    """Test ARIMA forecasting functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_profit = 150000
        self.historical_data = generate_seasonal_historical_data(self.base_profit, months=24, season='kharif')
    
    def test_generate_seasonal_data(self):
        """Test seasonal data generation"""
        data = generate_seasonal_historical_data(100000, months=24, season='kharif')
        
        self.assertEqual(len(data), 24)
        self.assertTrue(all(isinstance(x, (int, float, np.number)) for x in data))
        self.assertTrue(all(x > 0 for x in data))
    
    def test_train_arima_model(self):
        """Test ARIMA model training"""
        model = train_arima_model(self.historical_data, order=(1, 1, 1))
        
        # Check that model has AIC attribute
        self.assertTrue(hasattr(model, 'aic'))
        self.assertIsNotNone(model.aic)
    
    def test_forecast_profits(self):
        """Test profit forecasting"""
        model = train_arima_model(self.historical_data, order=(1, 1, 1))
        forecast = forecast_profits(model, periods=12)
        
        # Check forecast structure
        self.assertIn('forecast', forecast)
        self.assertIn('average_forecast', forecast)
        self.assertIn('forecast_std', forecast)
        
        # Check number of forecast periods
        self.assertEqual(len(forecast['forecast']), 12)
        
        # Check forecast data structure
        for period_forecast in forecast['forecast']:
            self.assertIn('period', period_forecast)
            self.assertIn('predicted_profit', period_forecast)
            self.assertIn('confidence_lower', period_forecast)
            self.assertIn('confidence_upper', period_forecast)
            
            # Confidence interval should contain prediction
            self.assertLessEqual(period_forecast['confidence_lower'], period_forecast['predicted_profit'])
            self.assertLessEqual(period_forecast['predicted_profit'], period_forecast['confidence_upper'])
    
    def test_forecast_stability(self):
        """Test forecast stability calculation"""
        model = train_arima_model(self.historical_data, order=(1, 1, 1))
        forecast = forecast_profits(model, periods=12)
        forecast_values = np.array([f['predicted_profit'] for f in forecast['forecast']])
        
        # Check that forecast has reasonable standard deviation
        forecast_std = np.std(forecast_values)
        self.assertGreater(forecast_std, 0)


class TestRecommendationEngine(unittest.TestCase):
    """Test recommendation engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.soybean_metrics = {
            'total_yield': 4000,
            'total_revenue': 240000,
            'total_cost': 90000,
            'net_profit': 150000,
            'profit_margin': 62.5,
            'roi': 166.67,
            'profit_per_kg': 37.5
        }
        
        self.maize_metrics = {
            'total_yield': 10000,
            'total_revenue': 250000,
            'total_cost': 72000,
            'net_profit': 178000,
            'profit_margin': 71.2,
            'roi': 247.22,
            'profit_per_kg': 17.8
        }
        
        self.soybean_data = {'name': 'Soybean', 'land_area': 2}
        self.maize_data = {'name': 'Maize', 'land_area': 2}
        
        self.soybean_ease = get_cultivation_ease('Soybean')
        self.maize_ease = get_cultivation_ease('Maize')
        
        self.forecast_soybean = np.array([95000, 100000, 105000, 110000, 115000, 120000,
                                         125000, 130000, 135000, 140000, 145000, 150000])
        self.forecast_maize = np.array([150000, 155000, 160000, 165000, 170000, 175000,
                                       180000, 185000, 190000, 195000, 200000, 205000])
    
    def test_get_cultivation_ease(self):
        """Test cultivation ease retrieval"""
        soybean_ease = get_cultivation_ease('Soybean')
        self.assertEqual(soybean_ease['difficulty'], 4)
        
        maize_ease = get_cultivation_ease('Maize')
        self.assertEqual(maize_ease['difficulty'], 3)
        
        unknown_crop_ease = get_cultivation_ease('Unknown Crop')
        self.assertIn('difficulty', unknown_crop_ease)
    
    def test_generate_recommendation(self):
        """Test recommendation generation"""
        score_os, score_cp, reasons_os, reasons_cp = generate_recommendation(
            self.soybean_metrics, self.maize_metrics,
            self.soybean_data, self.maize_data,
            self.soybean_ease, self.maize_ease,
            self.forecast_soybean, self.forecast_maize
        )
        
        # Total scores should sum to 10
        self.assertAlmostEqual(score_os + score_cp, 10.0, places=1)
        
        # Check that reasons are provided
        self.assertTrue(len(reasons_os) > 0 or len(reasons_cp) > 0)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_format_currency(self):
        """Test currency formatting"""
        self.assertEqual(format_currency(150000), '₹150,000')
        self.assertEqual(format_currency(1500.5, decimal_places=2), '₹1,500.50')
        self.assertEqual(format_currency(0), '₹0')
    
    def test_format_percentage(self):
        """Test percentage formatting"""
        self.assertEqual(format_percentage(62.5), '62.50%')
        self.assertEqual(format_percentage(166.67, decimal_places=1), '166.7%')
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        # Clean string should remain unchanged
        clean = sanitize_string('Soybean')
        self.assertEqual(clean, 'Soybean')
        
        # String with special characters should be cleaned
        dirty = sanitize_string('Soy@bean#crop!')
        self.assertEqual(dirty, 'Soybeancroph')
    
    def test_calculate_percentage_change(self):
        """Test percentage change calculation"""
        change = calculate_percentage_change(100, 120)
        self.assertEqual(change, 20.0)
        
        change = calculate_percentage_change(150000, 178000)
        self.assertAlmostEqual(change, 18.67, places=1)
    
    def test_get_risk_level(self):
        """Test risk level assessment"""
        low_std = 10000
        high_mean = 150000
        risk = get_risk_level(low_std, high_mean)
        self.assertEqual(risk['level'], 'Very Low')
        
        high_std = 80000
        risk = get_risk_level(high_std, high_mean)
        self.assertEqual(risk['level'], 'High')


class TestFlaskAPI(unittest.TestCase):
    """Test Flask API endpoints"""
    
    def setUp(self):
        """Set up Flask test client"""
        self.app = Flask(__name__)
        register_dashboard_routes(self.app)
        self.client = self.app.test_client()
    
    def test_predict_profit_endpoint(self):
        """Test /api/predict-profit endpoint"""
        payload = {
            'oilseed_name': 'Soybean',
            'oilseed_area': 2,
            'oilseed_yield': 2000,
            'oilseed_price': 60,
            'oilseed_cost': 45000,
            'crop_name': 'Maize',
            'crop_area': 2,
            'crop_yield': 5000,
            'crop_price': 25,
            'crop_cost': 36000
        }
        
        response = self.client.post('/api/predict-profit',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('oilseed', data)
        self.assertIn('crop', data)
        self.assertIn('comparison', data)
    
    def test_predict_profit_invalid_input(self):
        """Test /api/predict-profit with invalid input"""
        payload = {
            'oilseed_name': 'Soybean',
            'oilseed_area': -1,  # Invalid: negative area
            'oilseed_yield': 2000,
            'oilseed_price': 60,
            'oilseed_cost': 45000,
            'crop_name': 'Maize',
            'crop_area': 2,
            'crop_yield': 5000,
            'crop_price': 25,
            'crop_cost': 36000
        }
        
        response = self.client.post('/api/predict-profit',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_forecast_arima_endpoint(self):
        """Test /api/forecast-arima endpoint"""
        payload = {
            'oilseed_name': 'Soybean',
            'oilseed_base_profit': 150000,
            'crop_name': 'Maize',
            'crop_base_profit': 178000,
            'forecast_months': 12,
            'arima_order': [1, 1, 1]
        }
        
        response = self.client.post('/api/forecast-arima',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('oilseed_forecast', data)
        self.assertIn('crop_forecast', data)
    
    def test_recommend_crop_endpoint(self):
        """Test /api/recommend-crop endpoint"""
        payload = {
            'oilseed_name': 'Soybean',
            'oilseed_area': 2,
            'oilseed_yield': 2000,
            'oilseed_price': 60,
            'oilseed_cost': 45000,
            'crop_name': 'Maize',
            'crop_area': 2,
            'crop_yield': 5000,
            'crop_price': 25,
            'crop_cost': 36000
        }
        
        response = self.client.post('/api/recommend-crop',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('recommendation', data)
        self.assertIn('recommendation_score', data)
        self.assertIn('reasoning', data)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
