"""
Crop Economics & Market Pricing Routes
Provides real-time average prices for oilseeds and other crops
"""

from flask import Blueprint, render_template, jsonify, session
from functools import wraps
from datetime import datetime, timedelta
from extensions import db
from models_marketplace import SellRequest, CropListing

crop_economics_bp = Blueprint('crop_economics', __name__, url_prefix='/crop-economics')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'farmer_id_verified' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Common oilseeds in India
OILSEEDS = {
    'soybean': {'name': 'Soybean', 'unit': 'per quintal', 'icon': '🫘'},
    'mustard': {'name': 'Mustard', 'unit': 'per quintal', 'icon': '🌾'},
    'groundnut': {'name': 'Groundnut', 'unit': 'per quintal', 'icon': '🫘'},
    'sunflower': {'name': 'Sunflower', 'unit': 'per quintal', 'icon': '🌻'},
    'safflower': {'name': 'Safflower', 'unit': 'per quintal', 'icon': '🌻'},
    'sesame': {'name': 'Sesame', 'unit': 'per kg', 'icon': '🌾'},
    'coconut': {'name': 'Coconut', 'unit': 'per piece', 'icon': '🥥'},
}

@crop_economics_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Serve crop economics dashboard page"""
    return render_template('crop_economics.html', oilseeds=OILSEEDS)

@crop_economics_bp.route('/api/prices', methods=['GET'])
@login_required
def get_prices():
    """
    Get average prices for all oilseeds based on active sell requests
    Returns: {crop_name: {average: price, count: num_listings, max: price, min: price}}
    """
    prices = {}
    
    for crop_key, crop_info in OILSEEDS.items():
        # Query all active sell requests for this crop (case-insensitive)
        sell_requests = db.session.query(SellRequest).filter(
            db.func.lower(SellRequest.crop_name) == crop_key.lower()
        ).all()
        
        crop_listings = db.session.query(CropListing).filter(
            db.func.lower(CropListing.crop_name) == crop_key.lower()
        ).all()
        
        # Combine all prices
        all_prices = []
        
        for sr in sell_requests:
            if sr.expected_price:
                all_prices.append(float(sr.expected_price))
        
        for cl in crop_listings:
            if cl.expected_price:
                all_prices.append(float(cl.expected_price))
        
        # Calculate statistics
        if all_prices:
            avg_price = sum(all_prices) / len(all_prices)
            max_price = max(all_prices)
            min_price = min(all_prices)
            
            prices[crop_key] = {
                'crop_name': crop_info['name'],
                'average': round(avg_price, 2),
                'max': round(max_price, 2),
                'min': round(min_price, 2),
                'count': len(all_prices),
                'unit': crop_info['unit'],
                'icon': crop_info['icon'],
                'trend': 'stable'  # Could be calculated from historical data
            }
        else:
            # No data yet - show placeholder
            prices[crop_key] = {
                'crop_name': crop_info['name'],
                'average': 0,
                'max': 0,
                'min': 0,
                'count': 0,
                'unit': crop_info['unit'],
                'icon': crop_info['icon'],
                'trend': 'no_data'
            }
    
    return jsonify(prices)

@crop_economics_bp.route('/api/price-history/<crop>', methods=['GET'])
@login_required
def get_price_history(crop):
    """
    Get simulated price history for a crop (for trend line)
    In production, this would query historical data from database
    """
    crop_lower = crop.lower()
    
    if crop_lower not in OILSEEDS:
        return jsonify({'error': 'Crop not found'}), 404
    
    # Get current average price
    sell_requests = db.session.query(SellRequest).filter(
        db.func.lower(SellRequest.crop_name) == crop_lower
    ).all()
    
    crop_listings = db.session.query(CropListing).filter(
        db.func.lower(CropListing.crop_name) == crop_lower
    ).all()
    
    all_prices = []
    for sr in sell_requests:
        if sr.expected_price:
            all_prices.append(float(sr.expected_price))
    for cl in crop_listings:
        if cl.expected_price:
            all_prices.append(float(cl.expected_price))
    
    current_avg = sum(all_prices) / len(all_prices) if all_prices else 0
    
    # Generate simulated historical data (7 days)
    history = []
    for i in range(7, 0, -1):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        # Simulate variance
        variance = current_avg * (0.05 * (i % 3 - 1))  # ±5% variance
        price = max(current_avg + variance, 0)
        history.append({
            'date': date,
            'price': round(price, 2)
        })
    
    return jsonify({
        'crop': OILSEEDS[crop_lower]['name'],
        'history': history
    })

@crop_economics_bp.route('/api/comparison', methods=['GET'])
@login_required
def get_comparison():
    """
    Get price comparison across multiple crops for the comparison chart
    """
    comparison = []
    
    for crop_key, crop_info in OILSEEDS.items():
        sell_requests = db.session.query(SellRequest).filter(
            db.func.lower(SellRequest.crop_name) == crop_key.lower()
        ).all()
        
        crop_listings = db.session.query(CropListing).filter(
            db.func.lower(CropListing.crop_name) == crop_key.lower()
        ).all()
        
        all_prices = []
        for sr in sell_requests:
            if sr.expected_price:
                all_prices.append(float(sr.expected_price))
        for cl in crop_listings:
            if cl.expected_price:
                all_prices.append(float(cl.expected_price))
        
        if all_prices:
            avg_price = sum(all_prices) / len(all_prices)
            comparison.append({
                'crop': crop_info['name'],
                'price': round(avg_price, 2),
                'icon': crop_info['icon']
            })
    
    return jsonify(comparison)

@crop_economics_bp.route('/api/top-crops', methods=['GET'])
@login_required
def get_top_crops():
    """
    Get top oilseeds by listing count
    """
    crop_counts = {}
    
    for crop_key, crop_info in OILSEEDS.items():
        sell_requests_count = db.session.query(SellRequest).filter(
            db.func.lower(SellRequest.crop_name) == crop_key.lower()
        ).count()
        
        crop_listings_count = db.session.query(CropListing).filter(
            db.func.lower(CropListing.crop_name) == crop_key.lower()
        ).count()
        
        total_count = sell_requests_count + crop_listings_count
        
        if total_count > 0:
            crop_counts[crop_key] = {
                'name': crop_info['name'],
                'count': total_count,
                'icon': crop_info['icon']
            }
    
    # Sort by count and return top 5
    top_crops = sorted(crop_counts.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
    
    return jsonify([
        {
            'crop': info['name'],
            'listings': info['count'],
            'icon': info['icon']
        }
        for _, info in top_crops
    ])
