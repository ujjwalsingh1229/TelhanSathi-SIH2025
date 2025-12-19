"""
Configuration file for Farmer Dashboard Backend

Contains all configurable parameters:
- ARIMA model parameters
- Scoring weights
- Cultivation difficulty factors
- Database settings
- API settings
"""

# ============ ARIMA FORECASTING CONFIGURATION ============

# ARIMA model order (p, d, q)
# p: AR order (autoregressive)
# d: I order (differencing)
# q: MA order (moving average)
ARIMA_ORDER = (1, 1, 1)

# Number of months to forecast ahead
FORECAST_PERIODS = 12

# Confidence level for forecast intervals (0.05 = 95% confidence)
CONFIDENCE_LEVEL = 0.05

# Number of historical months to use for training
TRAINING_MONTHS = 24

# Seasonal patterns (mapping month to season)
SEASON_MAPPING = {
    1: 'winter',      # January
    2: 'winter',      # February
    3: 'spring',      # March
    4: 'spring',      # April
    5: 'summer',      # May
    6: 'summer',      # June
    7: 'monsoon',     # July
    8: 'monsoon',     # August
    9: 'autumn',      # September
    10: 'autumn',     # October
    11: 'winter',     # November
    12: 'winter'      # December
}

# Seasonal multipliers for synthetic data generation
SEASONAL_MULTIPLIERS = {
    'kharif': {'base': 1.0, 'variation': 0.15},      # Monsoon crops
    'rabi': {'base': 1.1, 'variation': 0.12},        # Winter crops
    'summer': {'base': 0.9, 'variation': 0.18},      # Summer crops
    'whole_year': {'base': 1.0, 'variation': 0.10}   # Year-round crops
}

# ============ RECOMMENDATION SCORING WEIGHTS ============

# Scoring weights (total = 10 points)
SCORING_WEIGHTS = {
    'net_profit': 0.30,           # Net Profit: 30% (3.0 points max)
    'roi': 0.25,                  # ROI: 25% (2.5 points max)
    'profit_margin': 0.20,        # Profit Margin: 20% (2.0 points max)
    'cultivation_ease': 0.15,     # Cultivation Ease: 15% (1.5 points max)
    'forecast_stability': 0.10    # Forecast Stability: 10% (1.0 point max)
}

# Score interpretation
SCORE_INTERPRETATION = {
    'excellent': (8.0, 10.0),
    'very_good': (6.0, 8.0),
    'good': (4.0, 6.0),
    'fair': (2.0, 4.0),
    'poor': (0.0, 2.0)
}

# ============ CULTIVATION DIFFICULTY FACTORS ============

# Cultivation difficulty database (0-10 scale)
CULTIVATION_FACTORS = {
    'Soybean': {'difficulty': 4, 'water_requirement': 'Moderate', 'labor': 'Low-Moderate', 'pests': 'Moderate', 'market_access': 'High'},
    'Groundnut': {'difficulty': 5, 'water_requirement': 'Low', 'labor': 'Moderate', 'pests': 'High', 'market_access': 'High'},
    'Mustard': {'difficulty': 3, 'water_requirement': 'Low', 'labor': 'Low', 'pests': 'Low', 'market_access': 'High'},
    'Sunflower': {'difficulty': 4, 'water_requirement': 'Moderate', 'labor': 'Low', 'pests': 'Moderate', 'market_access': 'High'},
    'Sesame': {'difficulty': 5, 'water_requirement': 'Low', 'labor': 'Moderate', 'pests': 'Moderate', 'market_access': 'Medium'},
    'Castor': {'difficulty': 3, 'water_requirement': 'Low', 'labor': 'Low', 'pests': 'Low', 'market_access': 'Medium'},
    'Linseed': {'difficulty': 3, 'water_requirement': 'Low', 'labor': 'Low', 'pests': 'Low', 'market_access': 'Medium'},
    'Rapeseed': {'difficulty': 3, 'water_requirement': 'Low', 'labor': 'Low', 'pests': 'Low', 'market_access': 'Medium'},
    'Safflower': {'difficulty': 4, 'water_requirement': 'Low', 'labor': 'Low', 'pests': 'Moderate', 'market_access': 'Low'},
    'Niger_Seed': {'difficulty': 3, 'water_requirement': 'Low', 'labor': 'Low', 'pests': 'Low', 'market_access': 'Low'},
    'Maize': {'difficulty': 3, 'water_requirement': 'High', 'labor': 'Moderate', 'pests': 'High', 'market_access': 'High'},
    'Wheat': {'difficulty': 2, 'water_requirement': 'Low', 'labor': 'Low', 'pests': 'Low', 'market_access': 'High'},
    'Rice': {'difficulty': 6, 'water_requirement': 'Very High', 'labor': 'High', 'pests': 'High', 'market_access': 'High'},
    'Cotton': {'difficulty': 7, 'water_requirement': 'High', 'labor': 'High', 'pests': 'Very High', 'market_access': 'High'},
}

# Default cultivation factors for unknown crops
DEFAULT_CULTIVATION_FACTORS = {
    'difficulty': 4,
    'water_requirement': 'Moderate',
    'labor': 'Moderate',
    'pests': 'Moderate',
    'market_access': 'High'
}

# ============ INPUT VALIDATION PARAMETERS ============

# Minimum and maximum values for input validation
INPUT_CONSTRAINTS = {
    'land_area': {
        'min': 0.01,
        'max': 100,
        'unit': 'hectares'
    },
    'expected_yield': {
        'min': 0,
        'max': 50000,
        'unit': 'kg/hectare'
    },
    'market_price': {
        'min': 0,
        'max': 1000,
        'unit': '₹/kg'
    },
    'total_cost_per_hectare': {
        'min': 0,
        'max': 500000,
        'unit': '₹'
    }
}

# ============ DATABASE CONFIGURATION ============

# SQLAlchemy database URI
DATABASE_URI = 'sqlite:///farmer_dashboard.db'

# Alternative: PostgreSQL
# DATABASE_URI = 'postgresql://user:password@localhost/farmer_dashboard'

# Database table names
DB_TABLES = {
    'farmer_inputs': 'farmer_inputs',
    'profit_results': 'profit_results',
    'forecast_results': 'forecast_results'
}

# ============ API CONFIGURATION ============

# API response settings
API_CONFIG = {
    'json_sort_keys': True,
    'json_compact': False,
    'pagination_limit': 100,
    'pagination_default': 20
}

# Rate limiting
RATE_LIMIT = {
    'enabled': True,
    'calls': 100,
    'per_seconds': 60  # 100 calls per 60 seconds
}

# ============ LOGGING CONFIGURATION ============

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'standard',
            'filename': 'farmer_dashboard.log'
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# ============ SECURITY CONFIGURATION ============

# CORS settings
CORS_CONFIG = {
    'origins': ['*'],
    'methods': ['GET', 'POST', 'PUT', 'DELETE'],
    'allow_headers': ['Content-Type', 'Authorization']
}

# Input sanitization
SECURITY_CONFIG = {
    'max_string_length': 100,
    'max_list_length': 1000,
    'validate_all_inputs': True
}

# ============ CURRENCY & FORMATTING ============

# Currency formatting
CURRENCY_CONFIG = {
    'symbol': '₹',
    'decimal_places': 0,
    'separator': ','
}

# Percentage formatting
PERCENTAGE_CONFIG = {
    'decimal_places': 2,
    'symbol': '%'
}

# ============ DEFAULT VALUES ============

# Default crop parameters if not provided
DEFAULT_CROP_PARAMS = {
    'Soybean': {
        'expected_yield': 2000,
        'market_price': 60,
        'total_cost_per_hectare': 45000
    },
    'Groundnut': {
        'expected_yield': 1500,
        'market_price': 80,
        'total_cost_per_hectare': 50000
    },
    'Mustard': {
        'expected_yield': 1200,
        'market_price': 100,
        'total_cost_per_hectare': 40000
    },
    'Sunflower': {
        'expected_yield': 1800,
        'market_price': 70,
        'total_cost_per_hectare': 42000
    },
    'Maize': {
        'expected_yield': 5000,
        'market_price': 25,
        'total_cost_per_hectare': 36000
    },
    'Wheat': {
        'expected_yield': 5000,
        'market_price': 20,
        'total_cost_per_hectare': 28000
    },
    'Rice': {
        'expected_yield': 6000,
        'market_price': 25,
        'total_cost_per_hectare': 55000
    }
}

# ============ FEATURE FLAGS ============

FEATURES = {
    'enable_arima_forecasting': True,
    'enable_recommendations': True,
    'enable_comparative_analysis': True,
    'enable_historical_data_caching': True,
    'enable_database_logging': True
}

# ============ PERFORMANCE SETTINGS ============

PERFORMANCE = {
    'cache_ttl_seconds': 3600,          # Cache time-to-live
    'max_forecast_periods': 24,         # Maximum months to forecast
    'min_historical_data': 12,          # Minimum months required for training
    'batch_processing_size': 100
}
