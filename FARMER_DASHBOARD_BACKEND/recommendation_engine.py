import numpy as np

# Cultivation factors database
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


def get_cultivation_ease(crop_name):
    """
    Get cultivation difficulty factors for a crop
    
    Args:
        crop_name (str): Name of the crop
    
    Returns:
        dict: Cultivation factors, or default if not found
    """
    return CULTIVATION_FACTORS.get(crop_name, {
        'difficulty': 4,
        'water_requirement': 'Moderate',
        'labor': 'Moderate',
        'pests': 'Moderate',
        'market_access': 'High'
    })


def generate_recommendation(oilseed_metrics, crop_metrics, oilseed_data, crop_data,
                           oilseed_ease, crop_ease, forecast_oilseed, forecast_crop):
    """
    Generate comprehensive farming recommendation based on multiple criteria
    
    Scoring Weights:
    - Net Profit: 30%
    - ROI: 25%
    - Profit Margin: 20%
    - Cultivation Ease: 15%
    - Forecast Stability: 10%
    
    Args:
        oilseed_metrics (dict): Oil seed profit metrics
        crop_metrics (dict): Crop profit metrics
        oilseed_data (dict): Oil seed crop data
        crop_data (dict): Crop data
        oilseed_ease (dict): Oil seed cultivation factors
        crop_ease (dict): Crop cultivation factors
        forecast_oilseed (np.array): Oil seed forecast values
        forecast_crop (np.array): Crop forecast values
    
    Returns:
        tuple: (score_oilseed, score_crop, reasons_oilseed, reasons_crop)
    """
    score_oilseed = 0.0
    score_crop = 0.0
    reasons_oilseed = []
    reasons_crop = []
    
    # 1. Net Profit Score (weight: 30%)
    if oilseed_metrics['net_profit'] > crop_metrics['net_profit']:
        profit_advantage = (oilseed_metrics['net_profit'] / crop_metrics['net_profit'] - 1) * 100
        score_oilseed += 3.0
        reasons_oilseed.append(f"✅ {profit_advantage:.1f}% higher net profit")
    else:
        profit_advantage = (crop_metrics['net_profit'] / oilseed_metrics['net_profit'] - 1) * 100
        score_crop += 3.0
        reasons_crop.append(f"✅ {profit_advantage:.1f}% higher net profit")
    
    # 2. ROI Score (weight: 25%)
    if oilseed_metrics['roi'] > crop_metrics['roi']:
        score_oilseed += 2.5
        reasons_oilseed.append(f"✅ Better ROI: {oilseed_metrics['roi']:.1f}% vs {crop_metrics['roi']:.1f}%")
    else:
        score_crop += 2.5
        reasons_crop.append(f"✅ Better ROI: {crop_metrics['roi']:.1f}% vs {oilseed_metrics['roi']:.1f}%")
    
    # 3. Profit Margin Score (weight: 20%)
    if oilseed_metrics['profit_margin'] > crop_metrics['profit_margin']:
        score_oilseed += 2.0
        reasons_oilseed.append(f"✅ Higher profit margin: {oilseed_metrics['profit_margin']:.1f}%")
    else:
        score_crop += 2.0
        reasons_crop.append(f"✅ Higher profit margin: {crop_metrics['profit_margin']:.1f}%")
    
    # 4. Cultivation Ease Score (weight: 15%)
    if oilseed_ease['difficulty'] <= crop_ease['difficulty']:
        score_oilseed += 1.5
        reasons_oilseed.append(f"✅ Easier cultivation (difficulty: {oilseed_ease['difficulty']}/10)")
    else:
        score_crop += 1.5
        reasons_crop.append(f"✅ Easier cultivation (difficulty: {crop_ease['difficulty']}/10)")
    
    # 5. Forecast Stability Score (weight: 10%)
    forecast_oilseed_np = forecast_oilseed if isinstance(forecast_oilseed, np.ndarray) else np.array(forecast_oilseed)
    forecast_crop_np = forecast_crop if isinstance(forecast_crop, np.ndarray) else np.array(forecast_crop)
    
    if forecast_oilseed is not None and forecast_crop is not None:
        oilseed_forecast_std = np.std(forecast_oilseed_np)
        crop_forecast_std = np.std(forecast_crop_np)
        if oilseed_forecast_std < crop_forecast_std:
            score_oilseed += 1.0
            reasons_oilseed.append("✅ More stable profit forecast")
        else:
            score_crop += 1.0
            reasons_crop.append("✅ More stable profit forecast")
    
    return score_oilseed, score_crop, reasons_oilseed, reasons_crop


def calculate_recommendation_score_breakdown(oilseed_metrics, crop_metrics,
                                             oilseed_ease, crop_ease,
                                             forecast_oilseed, forecast_crop):
    """
    Calculate detailed scoring breakdown
    
    Args:
        (same as generate_recommendation)
    
    Returns:
        dict: Detailed score breakdown for each factor
    """
    try:
        forecast_os_np = np.array(forecast_oilseed) if not isinstance(forecast_oilseed, np.ndarray) else forecast_oilseed
        forecast_cp_np = np.array(forecast_crop) if not isinstance(forecast_crop, np.ndarray) else forecast_crop
        
        breakdown = {
            'net_profit': {
                'oilseed': 3.0 if oilseed_metrics['net_profit'] > crop_metrics['net_profit'] else 0.0,
                'crop': 3.0 if crop_metrics['net_profit'] > oilseed_metrics['net_profit'] else 0.0,
                'factor': 'Net Profit',
                'weight': 0.30
            },
            'roi': {
                'oilseed': 2.5 if oilseed_metrics['roi'] > crop_metrics['roi'] else 0.0,
                'crop': 2.5 if crop_metrics['roi'] > oilseed_metrics['roi'] else 0.0,
                'factor': 'ROI',
                'weight': 0.25
            },
            'profit_margin': {
                'oilseed': 2.0 if oilseed_metrics['profit_margin'] > crop_metrics['profit_margin'] else 0.0,
                'crop': 2.0 if crop_metrics['profit_margin'] > oilseed_metrics['profit_margin'] else 0.0,
                'factor': 'Profit Margin',
                'weight': 0.20
            },
            'cultivation_ease': {
                'oilseed': 1.5 if oilseed_ease['difficulty'] <= crop_ease['difficulty'] else 0.0,
                'crop': 1.5 if crop_ease['difficulty'] < oilseed_ease['difficulty'] else 0.0,
                'factor': 'Cultivation Ease',
                'weight': 0.15
            },
            'forecast_stability': {
                'oilseed': 1.0 if np.std(forecast_os_np) < np.std(forecast_cp_np) else 0.0,
                'crop': 1.0 if np.std(forecast_cp_np) < np.std(forecast_os_np) else 0.0,
                'factor': 'Forecast Stability',
                'weight': 0.10
            }
        }
        return breakdown
    except Exception as e:
        raise ValueError(f"Error calculating score breakdown: {str(e)}")


def format_recommendation_output(score_os, score_cp, reasons_os, reasons_cp,
                                 oilseed_data, crop_data,
                                 oilseed_metrics, crop_metrics,
                                 oilseed_ease, crop_ease,
                                 forecast_mean_os, forecast_mean_cp):
    """
    Format recommendation output for API response
    
    Args:
        (same as generate_recommendation plus formatting params)
    
    Returns:
        dict: Formatted recommendation for JSON response
    """
    if score_os > score_cp:
        recommended = oilseed_data['name']
        score = score_os
        alt_score = score_cp
        reasons = reasons_os
        metrics = oilseed_metrics
        ease = oilseed_ease
        forecast_avg = np.mean(forecast_mean_os) if forecast_mean_os is not None else 0
    else:
        recommended = crop_data['name']
        score = score_cp
        alt_score = score_os
        reasons = reasons_cp
        metrics = crop_metrics
        ease = crop_ease
        forecast_avg = np.mean(forecast_mean_cp) if forecast_mean_cp is not None else 0
    
    return {
        'recommended_crop': recommended,
        'recommendation_score': round(score, 1),
        'alternative_score': round(alt_score, 1),
        'score_margin': round(score - alt_score, 1),
        'benefits': {
            'net_profit': f"₹{metrics['net_profit']:,.0f}",
            'roi': f"{metrics['roi']:.1f}%",
            'profit_margin': f"{metrics['profit_margin']:.1f}%",
            'difficulty': f"{ease['difficulty']}/10"
        },
        'estimated_12month_avg': f"₹{forecast_avg:,.0f}",
        'reasoning': reasons
    }
