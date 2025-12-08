from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sys
import os

# Avoid circular imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models_marketplace import Buyer
from extensions import db

buyer_auth_bp = Blueprint('buyer_auth', __name__, url_prefix='/buyer')

# ===== BUYER LOGIN ROUTES =====

@buyer_auth_bp.route('/login', methods=['GET'])
def buyer_login():
    """Render buyer login page"""
    return render_template('buyer_login.html')


@buyer_auth_bp.route('/login', methods=['POST'])
def buyer_login_post():
    """Handle buyer login"""
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    
    if not email or not password:
        return render_template('buyer_login.html', error='Email and password are required')
    
    # Find buyer by email
    buyer = Buyer.query.filter_by(email=email).first()
    
    if not buyer:
        return render_template('buyer_login.html', error='Email not found')
    
    # Check if buyer is active
    if not buyer.is_active:
        return render_template('buyer_login.html', error='This account has been deactivated')
    
    # Verify password
    if not check_password_hash(buyer.password, password):
        return render_template('buyer_login.html', error='Invalid password')
    
    # Set session
    session['buyer_id'] = buyer.id
    session['buyer_email'] = buyer.email
    session['buyer_name'] = buyer.buyer_name
    
    # Redirect to buyer dashboard
    return redirect(url_for('buyer_auth.buyer_dashboard'))


@buyer_auth_bp.route('/register', methods=['GET'])
def buyer_register():
    """Render buyer registration page"""
    return render_template('buyer_register.html')


@buyer_auth_bp.route('/register', methods=['POST'])
def buyer_register_post():
    """Handle buyer registration"""
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    buyer_name = request.form.get('buyer_name', '').strip()
    phone = request.form.get('phone', '').strip()
    company_name = request.form.get('company_name', '').strip()
    district = request.form.get('district', '').strip()
    state = request.form.get('state', 'Maharashtra').strip()
    
    # Validation
    if not email or not password or not buyer_name:
        return render_template('buyer_register.html', error='Email, password, and name are required')
    
    if password != confirm_password:
        return render_template('buyer_register.html', error='Passwords do not match')
    
    if len(password) < 6:
        return render_template('buyer_register.html', error='Password must be at least 6 characters')
    
    # Check if email already exists
    existing_buyer = Buyer.query.filter_by(email=email).first()
    if existing_buyer:
        return render_template('buyer_register.html', error='Email already registered')
    
    try:
        # Create new buyer
        buyer = Buyer(
            email=email,
            password=generate_password_hash(password),
            buyer_name=buyer_name,
            phone=phone,
            company_name=company_name,
            district=district,
            state=state,
            is_verified=True,
            is_active=True
        )
        
        db.session.add(buyer)
        db.session.commit()
        
        # Set session
        session['buyer_id'] = buyer.id
        session['buyer_email'] = buyer.email
        session['buyer_name'] = buyer.buyer_name
        
        # Redirect to dashboard
        return redirect(url_for('buyer_auth.buyer_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating buyer: {str(e)}")
        return render_template('buyer_register.html', error='Error creating account. Please try again.')


@buyer_auth_bp.route('/logout')
def buyer_logout():
    """Handle buyer logout"""
    session.clear()
    return redirect(url_for('buyer_auth.buyer_login'))


# ===== BUYER DASHBOARD =====

@buyer_auth_bp.route('/dashboard')
def buyer_dashboard():
    """Render buyer dashboard"""
    if 'buyer_id' not in session:
        return redirect(url_for('buyer_auth.buyer_login'))
    
    buyer = Buyer.query.filter_by(id=session.get('buyer_id')).first()
    if not buyer:
        session.clear()
        return redirect(url_for('buyer_auth.buyer_login'))
    
    return render_template('buyer_dashboard.html', buyer=buyer)


@buyer_auth_bp.route('/api/profile')
def buyer_profile():
    """Get buyer profile as JSON"""
    if 'buyer_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    buyer = Buyer.query.filter_by(id=session.get('buyer_id')).first()
    if not buyer:
        return jsonify({'error': 'Buyer not found'}), 404
    
    return jsonify({
        'id': buyer.id,
        'email': buyer.email,
        'buyer_name': buyer.buyer_name,
        'phone': buyer.phone,
        'company_name': buyer.company_name,
        'location': buyer.location,
        'district': buyer.district,
        'state': buyer.state,
        'is_verified': buyer.is_verified,
        'created_at': buyer.created_at.isoformat() if buyer.created_at else None
    })


@buyer_auth_bp.route('/api/deals')
def buyer_deals():
    """Get all deals (sell requests) for buyer to browse"""
    if 'buyer_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    # Import here to avoid circular imports
    from models_marketplace import SellRequest, SellPhoto
    
    # Get all sell requests
    deals = SellRequest.query.all()
    
    deals_data = []
    for deal in deals:
        photos = SellPhoto.query.filter_by(request_id=deal.id).all()
        deals_data.append({
            'id': deal.id,
            'crop_name': deal.crop_name,
            'quantity_quintal': deal.quantity_quintal,
            'expected_price': deal.expected_price,
            'location': deal.location,
            'harvest_date': deal.harvest_date,
            'farmer_name': deal.farmer_name,
            'farmer_phone': deal.farmer_phone,
            'status': deal.status,
            'photos': [{'id': p.id, 'photo_url': p.photo_url} for p in photos],
            'created_at': deal.created_at.isoformat() if deal.created_at else None
        })
    
    return jsonify(deals_data)


@buyer_auth_bp.route('/api/my-offers')
def buyer_my_offers():
    """Get buyer's own offers/deals"""
    if 'buyer_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    buyer_id = session.get('buyer_id')
    
    # Import here to avoid circular imports
    from models_marketplace import BuyerOffer, CropListing
    
    offers = BuyerOffer.query.filter_by(buyer_id=buyer_id).all()
    
    offers_data = []
    for offer in offers:
        listing = CropListing.query.get(offer.listing_id)
        offers_data.append({
            'id': offer.id,
            'listing_id': offer.listing_id,
            'crop_name': listing.crop_name if listing else 'Unknown',
            'initial_price': offer.initial_price,
            'final_price': offer.final_price,
            'status': offer.status,
            'created_at': offer.created_at.isoformat() if offer.created_at else None
        })
    
    return jsonify(offers_data)
