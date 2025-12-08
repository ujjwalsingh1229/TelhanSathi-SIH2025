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


@buyer_auth_bp.route('/api/my-offers')
def buyer_my_offers():
    """Get buyer's own offers (buyer-created independent offers)"""
    if 'buyer_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    buyer_id = session.get('buyer_id')
    
    # Import here to avoid circular imports
    from models_marketplace import BuyerOffer, SellRequest
    
    # Get all buyer offers for this buyer (independent offers, not linked to sell requests)
    offers = BuyerOffer.query.filter_by(buyer_id=buyer_id).all()
    
    offers_data = []
    for offer in offers:
        offer_dict = {
            'id': offer.id,
            'crop_name': offer.crop_name,
            'quantity_quintal': offer.quantity_quintal,
            'location_wanted': offer.location_wanted,
            'district_wanted': offer.district_wanted,
            'initial_price': offer.initial_price,
            'final_price': offer.final_price,
            'status': offer.status,
            'buyer_name': offer.buyer_name,
            'buyer_mobile': offer.buyer_mobile,
            'buyer_location': offer.buyer_location,
            'buyer_company': offer.buyer_company,
            'created_at': offer.created_at.isoformat() if offer.created_at else None,
            'updated_at': offer.updated_at.isoformat() if offer.updated_at else None,
            'sell_request': None
        }
        
        # If offer has been accepted, include the linked sell request
        if offer.sell_request_id:
            sell_req = SellRequest.query.get(offer.sell_request_id)
            if sell_req:
                offer_dict['sell_request'] = {
                    'id': sell_req.id,
                    'crop_name': sell_req.crop_name,
                    'quantity_quintal': sell_req.quantity_quintal,
                    'expected_price': sell_req.expected_price,
                    'farmer_name': sell_req.farmer_name,
                    'farmer_phone': sell_req.farmer_phone,
                    'location': sell_req.location,
                    'harvest_date': sell_req.harvest_date,
                    'status': sell_req.status,
                    'created_at': sell_req.created_at.isoformat() if sell_req.created_at else None
                }
        
        offers_data.append(offer_dict)
    
    return jsonify(offers_data)


@buyer_auth_bp.route('/api/create-offer', methods=['POST'])
def create_offer():
    """Create a new independent buyer offer (not linked to farmer's listing)"""
    if 'buyer_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        buyer_id = session.get('buyer_id')
        buyer_email = session.get('buyer_email')
        buyer_name = session.get('buyer_name')
        
        data = request.get_json()
        
        # Required fields
        crop_name = data.get('crop_name')
        quantity_quintal = data.get('quantity_quintal')
        initial_price = data.get('initial_price')
        
        # Optional fields
        location_wanted = data.get('location_wanted', '')
        district_wanted = data.get('district_wanted', '')
        
        # Validation
        if not crop_name or not quantity_quintal or not initial_price:
            return jsonify({'error': 'crop_name, quantity_quintal, and initial_price are required'}), 400
        
        # Validate quantity and price
        try:
            quantity_quintal = float(quantity_quintal)
            initial_price = float(initial_price)
            
            if quantity_quintal <= 0:
                return jsonify({'error': 'Quantity must be greater than 0'}), 400
            if initial_price <= 0:
                return jsonify({'error': 'Price must be greater than 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid quantity or price format'}), 400
        
        # Import models
        from models_marketplace import BuyerOffer, Buyer
        import uuid
        
        # Get buyer info
        buyer = Buyer.query.get(buyer_id)
        
        # Create new independent offer
        new_offer = BuyerOffer(
            id=str(uuid.uuid4()),
            buyer_id=buyer_id,
            buyer_name=buyer_name or (buyer.buyer_name if buyer else 'Unknown'),
            buyer_mobile=buyer.phone if buyer else '',
            buyer_location=buyer.location if buyer else '',
            buyer_company=buyer.company_name if buyer else '',
            crop_name=crop_name,
            quantity_quintal=quantity_quintal,
            location_wanted=location_wanted,
            district_wanted=district_wanted,
            initial_price=initial_price,
            final_price=None,
            status='pending'
        )
        
        db.session.add(new_offer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Offer created successfully! Farmers in the marketplace can now see your offer.',
            'offer': {
                'id': new_offer.id,
                'crop_name': new_offer.crop_name,
                'quantity_quintal': new_offer.quantity_quintal,
                'initial_price': new_offer.initial_price,
                'status': new_offer.status
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create offer: {str(e)}'}), 500


@buyer_auth_bp.route('/api/marketplace-offers')
def marketplace_offers():
    """Get all buyer offers available in the marketplace (for farmers to see)
    
    Optional query parameters:
    - crop_name: Filter by crop name
    - district: Filter by district_wanted
    - location: Filter by location_wanted
    """
    from models_marketplace import BuyerOffer
    
    # Get query parameters for filtering
    crop_name = request.args.get('crop_name', '').strip().lower()
    district = request.args.get('district', '').strip().lower()
    location = request.args.get('location', '').strip().lower()
    
    # Get all pending buyer offers (that haven't been accepted yet)
    query = BuyerOffer.query.filter_by(status='pending')
    
    # Apply filters if provided
    if crop_name:
        query = query.filter(BuyerOffer.crop_name.ilike(f'%{crop_name}%'))
    
    if district:
        query = query.filter(BuyerOffer.district_wanted.ilike(f'%{district}%'))
    
    if location:
        query = query.filter(BuyerOffer.location_wanted.ilike(f'%{location}%'))
    
    offers = query.all()
    
    offers_data = []
    for offer in offers:
        offers_data.append({
            'id': offer.id,
            'crop_name': offer.crop_name,
            'quantity_quintal': offer.quantity_quintal,
            'location_wanted': offer.location_wanted,
            'district_wanted': offer.district_wanted,
            'initial_price': offer.initial_price,
            'buyer_name': offer.buyer_name,
            'buyer_mobile': offer.buyer_mobile,
            'buyer_company': offer.buyer_company,
            'buyer_location': offer.buyer_location,
            'status': offer.status,
            'created_at': offer.created_at.isoformat() if offer.created_at else None
        })
    
    return jsonify(offers_data)
