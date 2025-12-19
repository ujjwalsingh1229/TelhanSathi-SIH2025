import pandas as pd
import numpy as np

def calculate_profit_metrics(crop_dict):
    """
    Calculate comprehensive profit metrics for a crop
    
    Args:
        crop_dict (dict): Contains 'land_area', 'expected_yield', 'market_price', 'total_cost_per_hectare'
    
    Returns:
        dict: Contains 'total_yield', 'total_revenue', 'total_cost', 'net_profit', 'profit_margin', 'roi'
    """
    try:
        land_area = crop_dict['land_area']
        yield_per_hectare = crop_dict['expected_yield']
        price_per_kg = crop_dict['market_price']
        total_cost_per_hectare = crop_dict['total_cost_per_hectare']
        
        # Revenue calculation
        total_yield = yield_per_hectare * land_area  # kg
        total_revenue = total_yield * price_per_kg  # ₹
        
        # Cost calculation
        total_cost = total_cost_per_hectare * land_area  # ₹
        
        # Profit calculation
        net_profit = total_revenue - total_cost  # ₹
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0  # %
        roi = (net_profit / total_cost * 100) if total_cost > 0 else 0  # %
        
        return {
            'total_yield': total_yield,
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'net_profit': net_profit,
            'profit_margin': profit_margin,
            'roi': roi,
            'revenue_per_kg': price_per_kg,
            'cost_per_kg': total_cost_per_hectare / yield_per_hectare,
            'profit_per_kg': (total_revenue - total_cost) / total_yield if total_yield > 0 else 0
        }
    except Exception as e:
        raise ValueError(f"Error calculating profit metrics: {str(e)}")


def compare_crops(oilseed_data, crop_data):
    """
    Compare two crops side-by-side
    
    Args:
        oilseed_data (dict): Oil seed crop parameters
        crop_data (dict): Traditional crop parameters
    
    Returns:
        dict: Comparison results with profit difference and percentage better
    """
    try:
        oilseed_metrics = calculate_profit_metrics(oilseed_data)
        crop_metrics = calculate_profit_metrics(crop_data)
        
        profit_diff = oilseed_metrics['net_profit'] - crop_metrics['net_profit']
        roi_diff = oilseed_metrics['roi'] - crop_metrics['roi']
        margin_diff = oilseed_metrics['profit_margin'] - crop_metrics['profit_margin']
        
        if profit_diff > 0:
            pct_better = (profit_diff / crop_metrics['net_profit'] * 100)
            more_profitable = oilseed_data['name']
        else:
            pct_better = (abs(profit_diff) / oilseed_metrics['net_profit'] * 100)
            more_profitable = crop_data['name']
        
        return {
            'oilseed_metrics': oilseed_metrics,
            'crop_metrics': crop_metrics,
            'profit_difference': profit_diff,
            'roi_difference': roi_diff,
            'margin_difference': margin_diff,
            'more_profitable': more_profitable,
            'percentage_better': pct_better
        }
    except Exception as e:
        raise ValueError(f"Error comparing crops: {str(e)}")


def validate_crop_input(crop_dict):
    """
    Validate crop input parameters
    
    Args:
        crop_dict (dict): Crop parameters to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['land_area', 'expected_yield', 'market_price', 'total_cost_per_hectare']
    
    for field in required_fields:
        if field not in crop_dict:
            return False, f"Missing required field: {field}"
        
        if not isinstance(crop_dict[field], (int, float)):
            return False, f"{field} must be numeric"
        
        if crop_dict[field] < 0:
            return False, f"{field} cannot be negative"
    
    if crop_dict['land_area'] == 0:
        return False, "Land area cannot be zero"
    
    if crop_dict['expected_yield'] == 0:
        return False, "Expected yield cannot be zero"
    
    if crop_dict['market_price'] == 0:
        return False, "Market price cannot be zero"
    
    return True, "Valid"


def format_currency(amount):
    """
    Format amount as Indian currency (₹)
    
    Args:
        amount (float): Amount to format
    
    Returns:
        str: Formatted currency string
    """
    return f"₹{amount:,.0f}"


def format_percentage(value):
    """
    Format value as percentage
    
    Args:
        value (float): Value to format
    
    Returns:
        str: Formatted percentage string
    """
    return f"{value:.2f}%"
