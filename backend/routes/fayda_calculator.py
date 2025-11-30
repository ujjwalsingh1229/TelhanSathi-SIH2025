"""
Module 1: Fayda Calculator (Profit Calculator)
Handles crop selection, land area input, and profit comparison
"""

from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
from datetime import datetime
from functools import wraps
import sys
import os

# Avoid circular imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Farmer, SubsidyApplication, PriceAlert
from extensions import db
from utils import is_farmer_eligible_for_subsidy, calculate_subsidy_amount

fayda_bp = Blueprint('fayda', __name__, url_prefix='/fayda')

# ===== AUTHENTICATION DECORATOR =====
def login_required(f):
    """Decorator to check if user is logged in (OTP verified)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'farmer_id_verified' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# ===== CROP DATABASE (Non-Oilseed Crops for Fayda Calculator) =====
CROPS_DATA = {
    # CEREALS
    'paddy': {
        'name_english': 'Paddy (Rice)',
        'name_hindi': 'धान',
        'category': 'Cereals',
        'icon': '🌾',
        'water_usage': 5,
        'cost_per_acre_low': 15000,
        'cost_per_acre_high': 18000,
        'yield_per_acre': 4500,
        'market_price': 20,
        'subsidy_available': False,
    },
    'wheat': {
        'name_english': 'Wheat',
        'name_hindi': 'गेहूँ',
        'category': 'Cereals',
        'icon': '🌾',
        'water_usage': 3,
        'cost_per_acre_low': 10000,
        'cost_per_acre_high': 12000,
        'yield_per_acre': 4200,
        'market_price': 22,
        'subsidy_available': False,
    },
    'maize': {
        'name_english': 'Maize (Corn)',
        'name_hindi': 'मक्का',
        'category': 'Cereals',
        'icon': '🌽',
        'water_usage': 4,
        'cost_per_acre_low': 12000,
        'cost_per_acre_high': 15000,
        'yield_per_acre': 4000,
        'market_price': 18,
        'subsidy_available': False,
    },
    'barley': {
        'name_english': 'Barley',
        'name_hindi': 'जौ',
        'category': 'Cereals',
        'icon': '🌾',
        'water_usage': 2,
        'cost_per_acre_low': 8000,
        'cost_per_acre_high': 10000,
        'yield_per_acre': 3800,
        'market_price': 18,
        'subsidy_available': False,
    },
    'sorghum': {
        'name_english': 'Sorghum',
        'name_hindi': 'ज्वार',
        'category': 'Cereals',
        'icon': '🌾',
        'water_usage': 2,
        'cost_per_acre_low': 7000,
        'cost_per_acre_high': 9000,
        'yield_per_acre': 3000,
        'market_price': 16,
        'subsidy_available': False,
    },
    'millets': {
        'name_english': 'Millets',
        'name_hindi': 'बाजरा',
        'category': 'Cereals',
        'icon': '🌾',
        'water_usage': 1,
        'cost_per_acre_low': 5000,
        'cost_per_acre_high': 7000,
        'yield_per_acre': 2000,
        'market_price': 15,
        'subsidy_available': False,
    },

    # PULSES
    'chickpea': {
        'name_english': 'Chickpeas',
        'name_hindi': 'चना',
        'category': 'Pulses',
        'icon': '🫘',
        'water_usage': 2,
        'cost_per_acre_low': 7000,
        'cost_per_acre_high': 9000,
        'yield_per_acre': 2500,
        'market_price': 50,
        'subsidy_available': False,
    },
    'lentil': {
        'name_english': 'Lentils',
        'name_hindi': 'दाल',
        'category': 'Pulses',
        'icon': '🫘',
        'water_usage': 2,
        'cost_per_acre_low': 6500,
        'cost_per_acre_high': 8500,
        'yield_per_acre': 2200,
        'market_price': 55,
        'subsidy_available': False,
    },
    'pigeonpea': {
        'name_english': 'Pigeon Peas',
        'name_hindi': 'अरहर',
        'category': 'Pulses',
        'icon': '🫘',
        'water_usage': 2,
        'cost_per_acre_low': 7000,
        'cost_per_acre_high': 9000,
        'yield_per_acre': 2300,
        'market_price': 60,
        'subsidy_available': False,
    },
    'bean': {
        'name_english': 'Dry Beans',
        'name_hindi': 'बीन',
        'category': 'Pulses',
        'icon': '🫘',
        'water_usage': 2,
        'cost_per_acre_low': 6000,
        'cost_per_acre_high': 8000,
        'yield_per_acre': 2000,
        'market_price': 48,
        'subsidy_available': False,
    },

    # ROOT & TUBER CROPS
    'potato': {
        'name_english': 'Potato',
        'name_hindi': 'आलू',
        'category': 'Root & Tuber',
        'icon': '🥔',
        'water_usage': 3,
        'cost_per_acre_low': 18000,
        'cost_per_acre_high': 22000,
        'yield_per_acre': 25000,
        'market_price': 15,
        'subsidy_available': False,
    },
    'sweetpotato': {
        'name_english': 'Sweet Potato',
        'name_hindi': 'शकरकंद',
        'category': 'Root & Tuber',
        'icon': '🧅',
        'water_usage': 3,
        'cost_per_acre_low': 15000,
        'cost_per_acre_high': 18000,
        'yield_per_acre': 20000,
        'market_price': 18,
        'subsidy_available': False,
    },

    # CASH CROPS
    'sugarcane': {
        'name_english': 'Sugarcane',
        'name_hindi': 'गन्ना',
        'category': 'Cash Crops',
        'icon': '🍃',
        'water_usage': 5,
        'cost_per_acre_low': 25000,
        'cost_per_acre_high': 30000,
        'yield_per_acre': 65,
        'market_price': 290,
        'subsidy_available': False,
    },
    'cotton': {
        'name_english': 'Cotton',
        'name_hindi': 'कपास',
        'category': 'Fiber Crops',
        'icon': '☁️',
        'water_usage': 4,
        'cost_per_acre_low': 20000,
        'cost_per_acre_high': 25000,
        'yield_per_acre': 15,
        'market_price': 5500,
        'subsidy_available': False,
    },

    # VEGETABLES
    'onion': {
        'name_english': 'Onion',
        'name_hindi': 'प्याज',
        'category': 'Vegetables',
        'icon': '🧅',
        'water_usage': 3,
        'cost_per_acre_low': 15000,
        'cost_per_acre_high': 20000,
        'yield_per_acre': 30000,
        'market_price': 18,
        'subsidy_available': False,
    },
    'tomato': {
        'name_english': 'Tomato',
        'name_hindi': 'टमाटर',
        'category': 'Vegetables',
        'icon': '🍅',
        'water_usage': 4,
        'cost_per_acre_low': 20000,
        'cost_per_acre_high': 25000,
        'yield_per_acre': 35000,
        'market_price': 15,
        'subsidy_available': False,
    },
    'carrot': {
        'name_english': 'Carrot',
        'name_hindi': 'गाजर',
        'category': 'Vegetables',
        'icon': '🥕',
        'water_usage': 2,
        'cost_per_acre_low': 12000,
        'cost_per_acre_high': 16000,
        'yield_per_acre': 28000,
        'market_price': 12,
        'subsidy_available': False,
    },

    # SPICES
    'turmeric': {
        'name_english': 'Turmeric',
        'name_hindi': 'हल्दी',
        'category': 'Spices',
        'icon': '🌟',
        'water_usage': 3,
        'cost_per_acre_low': 22000,
        'cost_per_acre_high': 28000,
        'yield_per_acre': 8000,
        'market_price': 80,
        'subsidy_available': False,
    },
    'ginger': {
        'name_english': 'Ginger',
        'name_hindi': 'अदरक',
        'category': 'Spices',
        'icon': '🌱',
        'water_usage': 3,
        'cost_per_acre_low': 20000,
        'cost_per_acre_high': 26000,
        'yield_per_acre': 7000,
        'market_price': 90,
        'subsidy_available': False,
    },
}

# ===== HELPER FUNCTIONS =====
def calculate_profit(crop_name, area_acres):
    """
    Calculate net profit for a given crop and land area
    Returns: {'gross_revenue': ..., 'total_cost': ..., 'net_profit': ..., 'subsidy': ...}
    """
    if crop_name not in CROPS_DATA:
        return None
    
    crop = CROPS_DATA[crop_name]
    
    # Calculate total cost (mid-range)
    avg_cost_per_acre = (crop['cost_per_acre_low'] + crop['cost_per_acre_high']) / 2
    total_cost = avg_cost_per_acre * area_acres
    
    # Calculate yield and revenue
    if crop_name == 'sugarcane':
        # Sugarcane yield is in tonnes
        total_yield = crop['yield_per_acre'] * area_acres
        gross_revenue = total_yield * crop['market_price']
    else:
        # Other crops yield is in kg
        total_yield = crop['yield_per_acre'] * area_acres
        gross_revenue = total_yield * crop['market_price']
    
    # Calculate subsidy
    subsidy = 0
    if crop['subsidy_available']:
        subsidy = crop['subsidy_amount'] * area_acres
        if crop_name == 'mustard':
            subsidy += crop['free_kit_value'] * area_acres
    
    # Net profit
    net_profit = gross_revenue - total_cost + subsidy
    
    return {
        'gross_revenue': round(gross_revenue, 2),
        'total_cost': round(total_cost, 2),
        'net_profit': round(net_profit, 2),
        'subsidy': round(subsidy, 2),
        'yield': round(total_yield, 2),
        'yield_unit': 'tonnes' if crop_name == 'sugarcane' else 'kg',
    }

# ===== ROUTES =====

@fayda_bp.route('/', methods=['GET'])
@login_required
def fayda_calculator():
    """Serve Fayda Calculator page - crop selection and land area input"""
    farmer_id = session.get('farmer_id_verified')
    farmer = Farmer.query.filter_by(id=farmer_id).first()
    
    if not farmer:
        return redirect(url_for('auth.login'))
    
    # Default values
    default_crop = 'paddy'  # Changed from soybean (oilseed) to paddy (cereal)
    default_area = farmer.total_land_area_hectares * 2.47 if farmer.total_land_area_hectares else 2.5  # Convert hectares to acres
    
    return render_template('fayda_calculator.html', 
                          farmer=farmer, 
                          crops=CROPS_DATA,
                          default_crop=default_crop,
                          default_area=round(default_area, 1))


@fayda_bp.route('/compare', methods=['POST'])
@login_required
def fayda_compare():
    """Calculate and compare profit for selected crop vs suggested crop"""
    farmer_id = session.get('farmer_id_verified')
    farmer = Farmer.query.filter_by(id=farmer_id).first()
    
    data = request.get_json()
    current_crop = data.get('current_crop', 'paddy')
    area_acres = float(data.get('area', 2.5))
    suggested_crop = data.get('suggested_crop', 'mustard')
    
    # Validate inputs
    if current_crop not in CROPS_DATA or suggested_crop not in CROPS_DATA:
        return jsonify({'error': 'Invalid crop selection'}), 400
    
    if area_acres <= 0 or area_acres > 100:
        return jsonify({'error': 'Invalid land area'}), 400
    
    # Calculate profits
    current_profit = calculate_profit(current_crop, area_acres)
    suggested_profit = calculate_profit(suggested_crop, area_acres)
    
    if not current_profit or not suggested_profit:
        return jsonify({'error': 'Could not calculate profit'}), 500
    
    # Calculate additional income
    additional_income = suggested_profit['net_profit'] - current_profit['net_profit']
    
    # Store comparison in session for later use
    session['fayda_comparison'] = {
        'current_crop': current_crop,
        'suggested_crop': suggested_crop,
        'area': area_acres,
        'current_profit': current_profit,
        'suggested_profit': suggested_profit,
        'additional_income': additional_income,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return jsonify({
        'success': True,
        'current_crop': {
            'name': CROPS_DATA[current_crop]['name_english'],
            'name_hindi': CROPS_DATA[current_crop]['name_hindi'],
            'profit': current_profit['net_profit'],
            'water_usage': CROPS_DATA[current_crop]['water_usage'],
            'yield': current_profit['yield'],
            'yield_unit': current_profit['yield_unit'],
            'subsidy': current_profit['subsidy'],
        },
        'suggested_crop': {
            'name': CROPS_DATA[suggested_crop]['name_english'],
            'name_hindi': CROPS_DATA[suggested_crop]['name_hindi'],
            'profit': suggested_profit['net_profit'],
            'water_usage': CROPS_DATA[suggested_crop]['water_usage'],
            'yield': suggested_profit['yield'],
            'yield_unit': suggested_profit['yield_unit'],
            'subsidy': suggested_profit['subsidy'],
        },
        'additional_income': additional_income,
        'area': area_acres,
    }), 200


@fayda_bp.route('/tulna', methods=['GET'])
@login_required
def fayda_tulna():
    """Serve Fayda Tulna (Comparison) page"""
    farmer_id = session.get('farmer_id_verified')
    farmer = Farmer.query.filter_by(id=farmer_id).first()
    
    # Get comparison data from session or redirect
    comparison = session.get('fayda_comparison')
    if not comparison:
        return redirect(url_for('fayda.fayda_calculator'))
    
    return render_template('fayda_tulna.html', 
                          farmer=farmer,
                          comparison=comparison,
                          crops=CROPS_DATA)


@fayda_bp.route('/extra-income', methods=['GET'])
@login_required
def extra_income():
    """Serve Extra Income visualization page"""
    farmer_id = session.get('farmer_id_verified')
    farmer = Farmer.query.filter_by(id=farmer_id).first()
    
    # Get comparison data from session
    comparison = session.get('fayda_comparison')
    if not comparison:
        return redirect(url_for('fayda.fayda_calculator'))
    
    return render_template('extra_income.html',
                          farmer=farmer,
                          comparison=comparison,
                          crops=CROPS_DATA)


@fayda_bp.route('/accept-suggestion', methods=['POST'])
@login_required
def accept_suggestion():
    """Accept crop suggestion and create subsidy application"""
    farmer_id = session.get('farmer_id_verified')
    farmer = Farmer.query.filter_by(id=farmer_id).first()
    
    if not farmer:
        return jsonify({'error': 'Farmer not found'}), 404
    
    comparison = session.get('fayda_comparison')
    if not comparison:
        return jsonify({'error': 'No comparison data'}), 400
    
    suggested_crop = comparison['suggested_crop']
    area_acres = comparison['area']
    
    # Create subsidy application using correct field names
    subsidy_app = SubsidyApplication(
        farmer_id=farmer.id,
        crop=suggested_crop.capitalize(),  # Use 'crop' field, not 'crop_name'
        application_date=datetime.utcnow(),
        status='pending',
        subsidy_amount=comparison['suggested_profit']['subsidy']
    )
    
    db.session.add(subsidy_app)
    
    # Mark farmer as oilseed farmer if they're adopting mustard/soybean
    if suggested_crop in ['mustard', 'soybean']:
        farmer.is_oilseed_farmer = True
        farmer.oilseed_enrollment_date = datetime.utcnow()
        # Update current crops
        farmer.current_crops = suggested_crop
    
    db.session.commit()
    
    # Clear comparison from session
    session.pop('fayda_comparison', None)
    
    return jsonify({
        'success': True,
        'message': f'Successfully applied for {CROPS_DATA[suggested_crop]["name_english"]} subsidy',
        'subsidy_app_id': subsidy_app.id,
        'subsidy_amount': subsidy_app.subsidy_amount,
        'is_oilseed_farmer': farmer.is_oilseed_farmer
    }), 201


@fayda_bp.route('/crop-details/<crop_name>', methods=['GET'])
@login_required
def crop_details(crop_name):
    """Get detailed information about a specific crop"""
    if crop_name not in CROPS_DATA:
        return jsonify({'error': 'Crop not found'}), 404
    
    crop = CROPS_DATA[crop_name]
    
    return jsonify({
        'name': crop['name_english'],
        'name_hindi': crop['name_hindi'],
        'water_usage': crop['water_usage'],
        'water_usage_label': ['Very Low', 'Low', 'Medium', 'High', 'Very High'][crop['water_usage'] - 1],
        'cost_per_acre_low': crop['cost_per_acre_low'],
        'cost_per_acre_high': crop['cost_per_acre_high'],
        'subsidy_available': crop['subsidy_available'],
        'subsidy_amount': crop.get('subsidy_amount', 0),
    }), 200

