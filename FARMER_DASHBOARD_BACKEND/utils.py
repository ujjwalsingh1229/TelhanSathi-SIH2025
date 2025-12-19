"""
Utility Functions for Farmer Dashboard Backend

Helper functions for:
- Data formatting and validation
- Currency and percentage formatting
- Input sanitization
- Common operations
"""

import re
from datetime import datetime
from config import CURRENCY_CONFIG, PERCENTAGE_CONFIG, INPUT_CONSTRAINTS, SECURITY_CONFIG


def format_currency(amount, symbol='₹', decimal_places=0):
    """
    Format amount as currency
    
    Args:
        amount (float): Amount to format
        symbol (str): Currency symbol (default: ₹)
        decimal_places (int): Decimal places (default: 0)
    
    Returns:
        str: Formatted currency string
    
    Examples:
        format_currency(150000) -> '₹150,000'
        format_currency(1500.5, decimal_places=2) -> '₹1,500.50'
    """
    if decimal_places == 0:
        formatted = f"{int(amount):,}"
    else:
        formatted = f"{amount:,.{decimal_places}f}"
    return f"{symbol}{formatted}"


def format_percentage(value, decimal_places=2, symbol='%'):
    """
    Format value as percentage
    
    Args:
        value (float): Value to format (e.g., 62.5 for 62.5%)
        decimal_places (int): Decimal places (default: 2)
        symbol (str): Symbol to append (default: %)
    
    Returns:
        str: Formatted percentage string
    
    Examples:
        format_percentage(62.5) -> '62.50%'
        format_percentage(166.67, decimal_places=1) -> '166.7%'
    """
    return f"{value:.{decimal_places}f}{symbol}"


def sanitize_string(value, max_length=100):
    """
    Sanitize string input to prevent injection attacks
    
    Args:
        value (str): String to sanitize
        max_length (int): Maximum allowed length
    
    Returns:
        str: Sanitized string
    
    Raises:
        ValueError: If string is invalid or too long
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")
    
    if len(value) > max_length:
        raise ValueError(f"String exceeds maximum length of {max_length}")
    
    # Remove leading/trailing whitespace
    value = value.strip()
    
    # Remove potentially harmful characters (keep alphanumeric, spaces, underscore, hyphen)
    value = re.sub(r'[^a-zA-Z0-9\s_\-]', '', value)
    
    return value


def sanitize_number(value, min_val=None, max_val=None):
    """
    Sanitize numeric input with bounds checking
    
    Args:
        value (float/int): Number to sanitize
        min_val (float): Minimum allowed value
        max_val (float): Maximum allowed value
    
    Returns:
        float: Sanitized number
    
    Raises:
        ValueError: If number is out of bounds
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Input must be numeric, got {value}")
    
    if min_val is not None and number < min_val:
        raise ValueError(f"Value {number} is less than minimum {min_val}")
    
    if max_val is not None and number > max_val:
        raise ValueError(f"Value {number} exceeds maximum {max_val}")
    
    return number


def validate_crop_input_values(crop_data):
    """
    Validate individual crop input fields
    
    Args:
        crop_data (dict): Crop data with keys:
            - land_area: hectares
            - expected_yield: kg/hectare
            - market_price: ₹/kg
            - total_cost_per_hectare: ₹
    
    Returns:
        tuple: (is_valid, error_message)
    
    Examples:
        validate_crop_input_values({'land_area': 2, 'expected_yield': 2000, 
                                   'market_price': 60, 'total_cost_per_hectare': 45000})
        -> (True, None)
    """
    errors = []
    
    # Validate land_area
    try:
        land_area = sanitize_number(
            crop_data.get('land_area'),
            min_val=INPUT_CONSTRAINTS['land_area']['min'],
            max_val=INPUT_CONSTRAINTS['land_area']['max']
        )
    except ValueError as e:
        errors.append(f"land_area: {str(e)}")
    
    # Validate expected_yield
    try:
        expected_yield = sanitize_number(
            crop_data.get('expected_yield'),
            min_val=INPUT_CONSTRAINTS['expected_yield']['min'],
            max_val=INPUT_CONSTRAINTS['expected_yield']['max']
        )
    except ValueError as e:
        errors.append(f"expected_yield: {str(e)}")
    
    # Validate market_price
    try:
        market_price = sanitize_number(
            crop_data.get('market_price'),
            min_val=INPUT_CONSTRAINTS['market_price']['min'],
            max_val=INPUT_CONSTRAINTS['market_price']['max']
        )
    except ValueError as e:
        errors.append(f"market_price: {str(e)}")
    
    # Validate total_cost_per_hectare
    try:
        total_cost = sanitize_number(
            crop_data.get('total_cost_per_hectare'),
            min_val=INPUT_CONSTRAINTS['total_cost_per_hectare']['min'],
            max_val=INPUT_CONSTRAINTS['total_cost_per_hectare']['max']
        )
    except ValueError as e:
        errors.append(f"total_cost_per_hectare: {str(e)}")
    
    if errors:
        return False, "; ".join(errors)
    
    return True, None


def parse_json_date(date_string):
    """
    Parse date string in ISO format (YYYY-MM-DD)
    
    Args:
        date_string (str): Date in ISO format
    
    Returns:
        datetime: Parsed datetime object
    
    Raises:
        ValueError: If date format is invalid
    
    Examples:
        parse_json_date('2024-01-15') -> datetime(2024, 1, 15)
    """
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Invalid date format: {date_string}. Use YYYY-MM-DD")


def format_json_date(date_obj):
    """
    Format datetime object to ISO string (YYYY-MM-DD)
    
    Args:
        date_obj (datetime): Datetime object
    
    Returns:
        str: Formatted date string
    
    Examples:
        format_json_date(datetime(2024, 1, 15)) -> '2024-01-15'
    """
    return date_obj.strftime('%Y-%m-%d')


def calculate_percentage_change(old_value, new_value):
    """
    Calculate percentage change between two values
    
    Args:
        old_value (float): Original value
        new_value (float): New value
    
    Returns:
        float: Percentage change
    
    Examples:
        calculate_percentage_change(100, 120) -> 20.0
        calculate_percentage_change(150000, 178000) -> 18.67
    """
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / abs(old_value)) * 100


def round_to_nearest(value, nearest=0):
    """
    Round value to nearest specified amount
    
    Args:
        value (float): Value to round
        nearest (int): Round to nearest (e.g., 100 for ₹100)
    
    Returns:
        float: Rounded value
    
    Examples:
        round_to_nearest(1250, 100) -> 1300
        round_to_nearest(1240, 100) -> 1200
    """
    if nearest == 0:
        return value
    return round(value / nearest) * nearest


def get_risk_level(forecast_std, forecast_mean):
    """
    Determine risk level based on forecast standard deviation
    
    Args:
        forecast_std (float): Standard deviation of forecast
        forecast_mean (float): Mean of forecast
    
    Returns:
        dict: Risk assessment with level and reasoning
    
    Risk levels:
    - Very Low: coefficient of variation < 10%
    - Low: coefficient of variation 10-20%
    - Moderate: coefficient of variation 20-30%
    - High: coefficient of variation 30-50%
    - Very High: coefficient of variation > 50%
    """
    if forecast_mean == 0:
        return {'level': 'Unknown', 'reasoning': 'Cannot calculate with zero mean'}
    
    cv = (forecast_std / abs(forecast_mean)) * 100
    
    if cv < 10:
        return {'level': 'Very Low', 'cv_percentage': round(cv, 2), 'reasoning': 'Highly stable forecast'}
    elif cv < 20:
        return {'level': 'Low', 'cv_percentage': round(cv, 2), 'reasoning': 'Stable forecast'}
    elif cv < 30:
        return {'level': 'Moderate', 'cv_percentage': round(cv, 2), 'reasoning': 'Moderately variable forecast'}
    elif cv < 50:
        return {'level': 'High', 'cv_percentage': round(cv, 2), 'reasoning': 'Highly variable forecast'}
    else:
        return {'level': 'Very High', 'cv_percentage': round(cv, 2), 'reasoning': 'Extremely volatile forecast'}


def calculate_roi(profit, cost):
    """
    Calculate Return on Investment (ROI)
    
    Args:
        profit (float): Net profit
        cost (float): Total cost
    
    Returns:
        float: ROI percentage
    
    Examples:
        calculate_roi(150000, 90000) -> 166.67
    """
    if cost == 0:
        return 0.0
    return (profit / cost) * 100


def calculate_profit_margin(revenue, profit):
    """
    Calculate profit margin percentage
    
    Args:
        revenue (float): Total revenue
        profit (float): Net profit
    
    Returns:
        float: Profit margin percentage
    
    Examples:
        calculate_profit_margin(240000, 150000) -> 62.5
    """
    if revenue == 0:
        return 0.0
    return (profit / revenue) * 100


def get_season_from_month(month):
    """
    Get season name from month number
    
    Args:
        month (int): Month number (1-12)
    
    Returns:
        str: Season name
    
    Mapping:
    - 1-2: winter
    - 3-4: spring
    - 5-6: summer
    - 7-8: monsoon
    - 9-10: autumn
    - 11-12: winter
    
    Examples:
        get_season_from_month(1) -> 'winter'
        get_season_from_month(8) -> 'monsoon'
    """
    if not isinstance(month, int) or month < 1 or month > 12:
        raise ValueError(f"Invalid month: {month}. Must be 1-12")
    
    if month in [1, 2, 11, 12]:
        return 'winter'
    elif month in [3, 4]:
        return 'spring'
    elif month in [5, 6]:
        return 'summer'
    elif month in [7, 8]:
        return 'monsoon'
    else:
        return 'autumn'


def get_month_name(month):
    """
    Get month name from month number
    
    Args:
        month (int): Month number (1-12)
    
    Returns:
        str: Month name
    """
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    
    if not isinstance(month, int) or month < 1 or month > 12:
        raise ValueError(f"Invalid month: {month}. Must be 1-12")
    
    return months[month - 1]


def create_error_response(error_message, status_code=400):
    """
    Create standardized error response
    
    Args:
        error_message (str): Error message
        status_code (int): HTTP status code
    
    Returns:
        tuple: (response_dict, status_code)
    
    Examples:
        create_error_response("Invalid input", 400)
        -> ({'success': False, 'error': 'Invalid input'}, 400)
    """
    return {
        'success': False,
        'error': error_message,
        'timestamp': datetime.now().isoformat()
    }, status_code


def create_success_response(data, message=None):
    """
    Create standardized success response
    
    Args:
        data (dict): Response data
        message (str): Optional success message
    
    Returns:
        dict: Response dictionary
    
    Examples:
        create_success_response({'profit': 150000})
        -> {'success': True, 'data': {'profit': 150000}, 'timestamp': '2024-01-15T...'}
    """
    return {
        'success': True,
        'data': data,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
