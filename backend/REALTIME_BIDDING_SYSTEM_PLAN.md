# Real-Time Bidding System for Mandi Connect - Complete Implementation Plan

## 🎯 Executive Summary

A real-time bidding system that allows **multiple buyers to bid simultaneously on farmer's crop listings** with live price updates, auction mechanics, and automatic deal closure. Based on Government's mandi price data for transparent pricing.

**Key Integration:**
- API: `Current Daily Price of Various Commodities from Various Markets (Mandi)`
- API Key: `579b464db66ec23bdd00000139dd36efa19740c954f95d9ca3b5abd0`
- Dataset: Ministry of Agriculture & Farmers Welfare

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    REAL-TIME BIDDING SYSTEM                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│   FARMER SIDE    │         │   BUYER SIDE     │
├──────────────────┤         ├──────────────────┤
│ • List Crop      │         │ • View Auctions  │
│ • Set Min Bid    │         │ • Place Bids     │
│ • Monitor Bids   │◄────────┤ • See Live Price │
│ • Accept Bid     │ WebSocket│ • Auto Bid       │
│ • Auction Status │         │ • Bid History    │
└──────────────────┘         └──────────────────┘
         ▲                              ▲
         │                              │
         └──────────┬───────────────────┘
                    │
         ┌──────────▼──────────┐
         │   WEBSOCKET SERVER  │
         │  (Real-time updates)│
         └─────────┬──────────┘
                    │
         ┌──────────▼──────────────────┐
         │   DATABASE LAYER             │
         ├──────────────────────────────┤
         │ • Auctions                   │
         │ • Bids                       │
         │ • Bid History                │
         │ • Transactions               │
         └──────────────────────────────┘
                    │
         ┌──────────▼──────────────────┐
         │   MANDI PRICE API            │
         │  (Base Price Reference)      │
         └──────────────────────────────┘
```

---

## 📦 Phase 1: Database Models & Schema

### 1.1 New Database Tables

#### **Auction Table**
```python
class Auction(db.Model):
    __tablename__ = "auctions"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Auction Details
    seller_id = db.Column(db.String(36), db.ForeignKey("farmers.id"), nullable=False)
    crop_name = db.Column(db.String(100), nullable=False)
    quantity_quintal = db.Column(db.Float, nullable=False)
    
    # Price Settings
    base_price = db.Column(db.Float, nullable=False)  # Mandi reference price
    min_bid_price = db.Column(db.Float, nullable=False)  # Farmer's minimum
    current_highest_bid = db.Column(db.Float, default=0)
    
    # Auction Duration
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=False)  # e.g., 24 hours from start
    status = db.Column(db.String(20), default="live")  # live, ended, sold, cancelled
    
    # Winning Bid
    winning_buyer_id = db.Column(db.String(36), db.ForeignKey("buyers.id"))
    final_price = db.Column(db.Float)
    
    # Photos & Description
    photo1_path = db.Column(db.String(255))
    photo2_path = db.Column(db.String(255))
    photo3_path = db.Column(db.String(255))
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bids = db.relationship('Bid', backref='auction', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='auction', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'crop_name': self.crop_name,
            'quantity': self.quantity_quintal,
            'base_price': self.base_price,
            'min_bid': self.min_bid_price,
            'current_bid': self.current_highest_bid,
            'time_left': self.get_time_remaining(),
            'status': self.status,
            'bidders_count': len(self.bids),
            'winning_buyer': self.winning_buyer_id
        }
    
    def get_time_remaining(self):
        """Returns seconds remaining in auction"""
        remaining = self.end_time - datetime.utcnow()
        return max(0, remaining.total_seconds())
    
    def is_active(self):
        return self.status == 'live' and self.get_time_remaining() > 0
```

#### **Bid Table**
```python
class Bid(db.Model):
    __tablename__ = "bids"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    auction_id = db.Column(db.String(36), db.ForeignKey("auctions.id"), nullable=False)
    buyer_id = db.Column(db.String(36), db.ForeignKey("buyers.id"), nullable=False)
    
    # Bid Details
    bid_amount = db.Column(db.Float, nullable=False)
    bid_type = db.Column(db.String(20), default="manual")  # manual, auto
    
    # For Auto-Bidding
    max_bid_amount = db.Column(db.Float)  # Maximum they're willing to pay
    auto_increment = db.Column(db.Float, default=100)  # Increment by ₹100
    
    # Status
    is_winning = db.Column(db.Boolean, default=False)
    is_outbid = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    outbid_at = db.Column(db.DateTime)  # When they were outbid
    
    # Relationships
    buyer = db.relationship('Buyer', backref='bids')
    
    def to_dict(self):
        return {
            'bid_id': self.id,
            'buyer_id': self.buyer_id,
            'amount': self.bid_amount,
            'type': self.bid_type,
            'is_winning': self.is_winning,
            'time': self.created_at.isoformat()
        }
```

#### **Transaction Table**
```python
class Transaction(db.Model):
    __tablename__ = "transactions"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    auction_id = db.Column(db.String(36), db.ForeignKey("auctions.id"), nullable=False)
    seller_id = db.Column(db.String(36), db.ForeignKey("farmers.id"), nullable=False)
    buyer_id = db.Column(db.String(36), db.ForeignKey("buyers.id"), nullable=False)
    
    # Transaction Details
    crop_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    final_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)  # quantity * final_price
    
    # Payment & Delivery
    status = db.Column(db.String(20), default="pending")  # pending, confirmed, paid, delivered, completed
    payment_method = db.Column(db.String(50))  # bank_transfer, upi, check, etc.
    payment_date = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'transaction_id': self.id,
            'crop': self.crop_name,
            'quantity': self.quantity,
            'price': self.final_price,
            'total': self.total_amount,
            'status': self.status,
            'date': self.created_at.isoformat()
        }
```

#### **Bid History (for audit trail)**
```python
class BidHistory(db.Model):
    __tablename__ = "bid_history"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    auction_id = db.Column(db.String(36), db.ForeignKey("auctions.id"), nullable=False)
    buyer_id = db.Column(db.String(36), db.ForeignKey("buyers.id"), nullable=False)
    
    old_bid = db.Column(db.Float)
    new_bid = db.Column(db.Float)
    action = db.Column(db.String(50))  # placed, outbid, withdrawn
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### 1.2 Migration Command
```bash
# In your Flask shell:
flask db migrate -m "Add real-time bidding system tables"
flask db upgrade
```

---

## 🔌 Phase 2: WebSocket Server Setup

### 2.1 Install Dependencies
```bash
pip install python-socketio
pip install python-engineio
pip install redis  # Optional: for production scaling
```

### 2.2 WebSocket Configuration (create `ml/websocket_server.py`)

```python
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import session
from extensions import db
from models_marketplace import Auction, Bid, BidHistory
from datetime import datetime
import json

socketio = SocketIO(cors_allowed_origins="*")

# Track active auction rooms
active_auctions = {}

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {session.get('user_id')}")
    emit('connection_response', {'data': 'Connected to bidding server'})

@socketio.on('join_auction')
def on_join_auction(data):
    """User joins an auction room for live updates"""
    auction_id = data['auction_id']
    user_id = session.get('farmer_id_verified') or session.get('buyer_id_verified')
    
    # Join user to auction room
    join_room(f"auction_{auction_id}")
    
    # Track active auctions
    if auction_id not in active_auctions:
        active_auctions[auction_id] = {
            'watchers': [],
            'start_time': datetime.utcnow()
        }
    
    active_auctions[auction_id]['watchers'].append(user_id)
    
    # Send auction state to this user
    auction = Auction.query.get(auction_id)
    if auction:
        emit('auction_state', {
            'auction': auction.to_dict(),
            'latest_bids': [bid.to_dict() for bid in Bid.query.filter_by(auction_id=auction_id).order_by(Bid.created_at.desc()).limit(10).all()]
        })

@socketio.on('place_bid')
def on_place_bid(data):
    """Handle new bid placement"""
    auction_id = data['auction_id']
    buyer_id = session.get('buyer_id_verified')
    bid_amount = float(data['bid_amount'])
    
    if not buyer_id:
        emit('error', {'message': 'Not authenticated as buyer'})
        return
    
    # Get auction
    auction = Auction.query.get(auction_id)
    if not auction or not auction.is_active():
        emit('error', {'message': 'Auction is not active'})
        return
    
    # Validate bid
    if bid_amount <= auction.current_highest_bid:
        emit('error', {'message': f'Bid must be higher than ₹{auction.current_highest_bid}'})
        return
    
    if bid_amount < auction.min_bid_price:
        emit('error', {'message': f'Bid must be at least ₹{auction.min_bid_price}'})
        return
    
    try:
        # Create new bid
        new_bid = Bid(
            auction_id=auction_id,
            buyer_id=buyer_id,
            bid_amount=bid_amount,
            bid_type='manual',
            is_winning=True
        )
        
        # Mark previous winning bid as outbid
        old_winning = Bid.query.filter_by(auction_id=auction_id, is_winning=True).first()
        if old_winning:
            old_winning.is_winning = False
            old_winning.is_outbid = True
            old_winning.outbid_at = datetime.utcnow()
        
        # Update auction
        auction.current_highest_bid = bid_amount
        auction.winning_buyer_id = buyer_id
        auction.updated_at = datetime.utcnow()
        
        # Save to database
        db.session.add(new_bid)
        db.session.commit()
        
        # Create bid history
        history = BidHistory(
            auction_id=auction_id,
            buyer_id=buyer_id,
            old_bid=old_winning.bid_amount if old_winning else 0,
            new_bid=bid_amount,
            action='placed'
        )
        db.session.add(history)
        db.session.commit()
        
        # Broadcast to all users in auction
        emit('bid_placed', {
            'bid': new_bid.to_dict(),
            'auction': auction.to_dict(),
            'message': f'New bid: ₹{bid_amount}'
        }, room=f"auction_{auction_id}")
        
        # Notify previous bidder they were outbid
        if old_winning and old_winning.buyer_id != buyer_id:
            emit('you_were_outbid', {
                'amount': bid_amount,
                'by_buyer': buyer_id
            }, room=f"buyer_{old_winning.buyer_id}")
        
    except Exception as e:
        print(f"Error placing bid: {str(e)}")
        emit('error', {'message': 'Error placing bid'})

@socketio.on('auto_bid')
def on_auto_bid(data):
    """Set up automatic bidding"""
    auction_id = data['auction_id']
    buyer_id = session.get('buyer_id_verified')
    max_amount = float(data['max_amount'])
    increment = float(data.get('increment', 100))
    
    if not buyer_id:
        emit('error', {'message': 'Not authenticated'})
        return
    
    auction = Auction.query.get(auction_id)
    if not auction:
        emit('error', {'message': 'Auction not found'})
        return
    
    # Create auto-bid
    auto_bid = Bid(
        auction_id=auction_id,
        buyer_id=buyer_id,
        bid_amount=auction.current_highest_bid + increment,
        bid_type='auto',
        max_bid_amount=max_amount,
        auto_increment=increment
    )
    
    db.session.add(auto_bid)
    db.session.commit()
    
    emit('auto_bid_activated', {
        'max_amount': max_amount,
        'increment': increment
    })

@socketio.on('end_auction')
def on_end_auction(data):
    """Farmer ends auction (can be called manually or by timer)"""
    auction_id = data['auction_id']
    auction = Auction.query.get(auction_id)
    
    if not auction:
        emit('error', {'message': 'Auction not found'})
        return
    
    # Mark auction as ended
    auction.status = 'ended'
    
    if auction.current_highest_bid >= auction.min_bid_price:
        auction.status = 'sold'
        auction.final_price = auction.current_highest_bid
        
        # Create transaction
        transaction = Transaction(
            auction_id=auction_id,
            seller_id=auction.seller_id,
            buyer_id=auction.winning_buyer_id,
            crop_name=auction.crop_name,
            quantity=auction.quantity_quintal,
            final_price=auction.final_price,
            total_amount=auction.quantity_quintal * auction.final_price
        )
        db.session.add(transaction)
    
    db.session.commit()
    
    # Notify all users
    emit('auction_ended', {
        'auction_id': auction_id,
        'status': auction.status,
        'winning_buyer': auction.winning_buyer_id,
        'final_price': auction.final_price
    }, room=f"auction_{auction_id}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {session.get('user_id')}")
```

### 2.3 Update `app.py` to Initialize WebSocket

```python
from flask_socketio import SocketIO
from ml.websocket_server import socketio

# In your Flask app initialization:
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# After creating app:
socketio.init_app(app)

# Run with:
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
```

---

## 🛣️ Phase 3: API Endpoints (Flask Routes)

Create new file: `routes/bidding.py`

```python
from flask import Blueprint, jsonify, request, session, render_template
from functools import wraps
from datetime import datetime, timedelta
from extensions import db
from models_marketplace import Auction, Bid, Transaction, BidHistory, Buyer
from models import Farmer
import requests

bidding_bp = Blueprint('bidding', __name__, url_prefix='/bidding')

# Government Mandi API Configuration
GOVT_API_KEY = "579b464db66ec23bdd00000139dd36efa19740c954f95d9ca3b5abd0"
GOVT_API_BASE = "https://api.data.gov.in/resource/9ef84268-d588-465a-a5c3-375cda092f58"

def farmer_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'farmer_id_verified' not in session:
            return jsonify({'error': 'Farmer not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function

def buyer_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'buyer_id_verified' not in session:
            return jsonify({'error': 'Buyer not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==================== FARMER ROUTES ====================

@bidding_bp.route('/farmer/create-auction', methods=['POST'])
@farmer_login_required
def create_auction():
    """Create new auction for crop"""
    farmer_id = session['farmer_id_verified']
    data = request.get_json()
    
    # Get base price from mandi API
    base_price = get_base_price(data['crop_name'])
    
    # Create auction
    auction = Auction(
        seller_id=farmer_id,
        crop_name=data['crop_name'],
        quantity_quintal=float(data['quantity']),
        base_price=base_price,
        min_bid_price=float(data['min_bid_price']),
        end_time=datetime.utcnow() + timedelta(hours=data.get('duration_hours', 24)),
        location=data.get('location'),
        description=data.get('description')
    )
    
    # Handle photo uploads
    if 'photos' in request.files:
        photos = request.files.getlist('photos')
        for idx, photo in enumerate(photos[:3]):
            if photo:
                filename = secure_filename(photo.filename)
                path = f"static/auction_photos/{uuid.uuid4()}_{filename}"
                photo.save(path)
                if idx == 0:
                    auction.photo1_path = path
                elif idx == 1:
                    auction.photo2_path = path
                elif idx == 2:
                    auction.photo3_path = path
    
    db.session.add(auction)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'auction_id': auction.id,
        'base_price': base_price,
        'message': 'Auction created successfully'
    }), 201

@bidding_bp.route('/farmer/my-auctions', methods=['GET'])
@farmer_login_required
def farmer_auctions():
    """Get farmer's all auctions"""
    farmer_id = session['farmer_id_verified']
    
    status_filter = request.args.get('status', 'all')
    
    query = Auction.query.filter_by(seller_id=farmer_id)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    auctions = query.order_by(Auction.created_at.desc()).all()
    
    return jsonify({
        'auctions': [auction.to_dict() for auction in auctions],
        'total': len(auctions)
    })

@bidding_bp.route('/farmer/auction/<auction_id>', methods=['GET'])
@farmer_login_required
def farmer_auction_detail(auction_id):
    """Get auction details with all bids"""
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.seller_id != session['farmer_id_verified']:
        return jsonify({'error': 'Not your auction'}), 403
    
    bids = Bid.query.filter_by(auction_id=auction_id).order_by(Bid.created_at.desc()).all()
    
    return jsonify({
        'auction': auction.to_dict(),
        'bids': [bid.to_dict() for bid in bids],
        'bid_count': len(bids),
        'unique_bidders': len(set(bid.buyer_id for bid in bids)),
        'bid_history': [
            {
                'buyer_id': bid.buyer_id,
                'amount': bid.bid_amount,
                'time': bid.created_at.isoformat(),
                'is_winning': bid.is_winning
            }
            for bid in bids
        ]
    })

@bidding_bp.route('/farmer/auction/<auction_id>/end', methods=['POST'])
@farmer_login_required
def end_auction(auction_id):
    """End auction (farmer manual end)"""
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.seller_id != session['farmer_id_verified']:
        return jsonify({'error': 'Not your auction'}), 403
    
    if auction.status != 'live':
        return jsonify({'error': 'Auction is not live'}), 400
    
    # End auction
    auction.status = 'ended'
    
    # Check if there are valid bids
    winning_bid = Bid.query.filter_by(auction_id=auction_id, is_winning=True).first()
    
    if winning_bid and winning_bid.bid_amount >= auction.min_bid_price:
        auction.status = 'sold'
        auction.final_price = winning_bid.bid_amount
        auction.winning_buyer_id = winning_bid.buyer_id
        
        # Create transaction
        transaction = Transaction(
            auction_id=auction_id,
            seller_id=auction.seller_id,
            buyer_id=winning_bid.buyer_id,
            crop_name=auction.crop_name,
            quantity=auction.quantity_quintal,
            final_price=winning_bid.bid_amount,
            total_amount=auction.quantity_quintal * winning_bid.bid_amount
        )
        db.session.add(transaction)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'status': auction.status,
        'message': 'Auction ended'
    })

# ==================== BUYER ROUTES ====================

@bidding_bp.route('/buyer/auctions', methods=['GET'])
@buyer_login_required
def buyer_browse_auctions():
    """Browse all active auctions"""
    # Filter parameters
    crop_filter = request.args.get('crop', None)
    max_price = request.args.get('max_price', None)
    sort_by = request.args.get('sort', 'newest')  # newest, price_low, price_high, ending_soon
    
    query = Auction.query.filter_by(status='live').filter(Auction.end_time > datetime.utcnow())
    
    if crop_filter:
        query = query.filter_by(crop_name=crop_filter)
    
    if max_price:
        query = query.filter(Auction.min_bid_price <= float(max_price))
    
    # Sorting
    if sort_by == 'newest':
        query = query.order_by(Auction.created_at.desc())
    elif sort_by == 'price_low':
        query = query.order_by(Auction.current_highest_bid.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Auction.current_highest_bid.desc())
    elif sort_by == 'ending_soon':
        query = query.order_by(Auction.end_time.asc())
    
    auctions = query.all()
    
    return jsonify({
        'auctions': [auction.to_dict() for auction in auctions],
        'total': len(auctions)
    })

@bidding_bp.route('/buyer/auction/<auction_id>', methods=['GET'])
@buyer_login_required
def buyer_auction_detail(auction_id):
    """Get auction details for buyer (with bid info)"""
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    buyer_id = session['buyer_id_verified']
    
    # Get buyer's bids
    my_bids = Bid.query.filter_by(auction_id=auction_id, buyer_id=buyer_id).all()
    
    # Get all bids (only showing count, not details for privacy)
    all_bids = Bid.query.filter_by(auction_id=auction_id).all()
    
    return jsonify({
        'auction': auction.to_dict(),
        'my_bids': [bid.to_dict() for bid in my_bids],
        'total_bids': len(all_bids),
        'unique_bidders': len(set(bid.buyer_id for bid in all_bids)),
        'my_status': {
            'is_winning': any(bid.is_winning for bid in my_bids),
            'highest_bid': max([bid.bid_amount for bid in my_bids]) if my_bids else 0
        }
    })

@bidding_bp.route('/buyer/my-bids', methods=['GET'])
@buyer_login_required
def buyer_my_bids():
    """Get buyer's bid history and status"""
    buyer_id = session['buyer_id_verified']
    
    # Get all bids by this buyer
    bids = Bid.query.filter_by(buyer_id=buyer_id).order_by(Bid.created_at.desc()).all()
    
    # Organize by auction
    auctions_dict = {}
    for bid in bids:
        if bid.auction_id not in auctions_dict:
            auction = Auction.query.get(bid.auction_id)
            auctions_dict[bid.auction_id] = {
                'auction': auction.to_dict() if auction else {},
                'bids': []
            }
        auctions_dict[bid.auction_id]['bids'].append(bid.to_dict())
    
    return jsonify({
        'auctions': list(auctions_dict.values()),
        'total_auctions': len(auctions_dict),
        'total_bids': len(bids)
    })

@bidding_bp.route('/buyer/won-auctions', methods=['GET'])
@buyer_login_required
def buyer_won_auctions():
    """Get auctions won by buyer"""
    buyer_id = session['buyer_id_verified']
    
    transactions = Transaction.query.filter_by(buyer_id=buyer_id).all()
    
    return jsonify({
        'transactions': [t.to_dict() for t in transactions],
        'total_won': len(transactions),
        'total_amount': sum(t.total_amount for t in transactions)
    })

# ==================== SHARED ROUTES ====================

@bidding_bp.route('/auction/<auction_id>/live-updates', methods=['GET'])
def auction_live_updates(auction_id):
    """Get live updates for auction (polling fallback)"""
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    return jsonify({
        'auction': auction.to_dict(),
        'latest_bid': Bid.query.filter_by(auction_id=auction_id, is_winning=True).first().to_dict() if Bid.query.filter_by(auction_id=auction_id, is_winning=True).first() else None
    })

@bidding_bp.route('/get-base-price/<crop>', methods=['GET'])
def get_base_price_endpoint(crop):
    """Get base price from mandi API"""
    price = get_base_price(crop)
    return jsonify({'crop': crop, 'base_price': price})

def get_base_price(crop_name):
    """Fetch base price from Government Mandi API"""
    try:
        params = {
            'api-key': GOVT_API_KEY,
            'format': 'json',
            'filters[commodity]': crop_name,
            'limit': 10,
            'sort': {'arrival_date': -1}
        }
        
        response = requests.get(GOVT_API_BASE, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'records' in data and len(data['records']) > 0:
                # Calculate average price
                prices = []
                for record in data['records']:
                    price = record.get('modal_price') or record.get('price') or 0
                    if price:
                        prices.append(float(price))
                
                if prices:
                    return sum(prices) / len(prices)
    except Exception as e:
        print(f"Error fetching base price: {str(e)}")
    
    # Default base prices if API fails
    default_prices = {
        'Soybean': 5500,
        'Mustard': 6200,
        'Groundnut': 7400,
        'Sunflower': 6800,
        'Safflower': 4900,
        'Sesame': 8200,
        'Coconut': 4500
    }
    
    return default_prices.get(crop_name, 5000)

@bidding_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get overall bidding system statistics"""
    active_auctions = Auction.query.filter_by(status='live').count()
    total_auctions = Auction.query.count()
    total_bids = Bid.query.count()
    completed_transactions = Transaction.query.filter_by(status='completed').count()
    
    return jsonify({
        'active_auctions': active_auctions,
        'total_auctions': total_auctions,
        'total_bids': total_bids,
        'completed_transactions': completed_transactions
    })
```

### Register in `app.py`:
```python
from routes.bidding import bidding_bp

app.register_blueprint(bidding_bp)
```

---

## 🎨 Phase 4: Frontend Implementation

### 4.1 Buyer Dashboard - Browse Auctions

Create: `templates/auction_browse.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>Live Auctions - TelhanSathi</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body { font-family: Arial; background: #f5f5f5; }
        .auction-container { max-width: 1200px; margin: 20px auto; }
        .filters { background: white; padding: 15px; margin-bottom: 20px; border-radius: 8px; }
        .auction-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .auction-card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .auction-image { width: 100%; height: 200px; background: #ddd; object-fit: cover; }
        .auction-info { padding: 15px; }
        .crop-name { font-size: 18px; font-weight: bold; color: #333; }
        .auction-details { font-size: 14px; color: #666; margin: 10px 0; }
        .price-section { background: #f9f9f9; padding: 10px; border-radius: 4px; margin: 10px 0; }
        .current-bid { font-size: 16px; font-weight: bold; color: #2ecc71; }
        .timer { color: #e74c3c; font-weight: bold; }
        .bid-button { width: 100%; padding: 10px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .bid-button:hover { background: #2980b9; }
        .live-badge { display: inline-block; background: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="auction-container">
        <h1>🎯 Live Auctions</h1>
        
        <!-- Filters -->
        <div class="filters">
            <input type="text" id="cropFilter" placeholder="Search by crop..." style="padding: 8px; width: 200px; margin-right: 10px;">
            <button onclick="loadAuctions()" style="padding: 8px 15px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer;">Filter</button>
        </div>
        
        <!-- Auction Grid -->
        <div class="auction-grid" id="auctionGrid">
            <p>Loading auctions...</p>
        </div>
    </div>

    <script>
        const socket = io();
        let currentAuctions = {};

        // Load all active auctions
        function loadAuctions() {
            const crop = document.getElementById('cropFilter').value;
            const url = `/bidding/buyer/auctions?sort=ending_soon${crop ? '&crop=' + crop : ''}`;
            
            fetch(url)
                .then(r => r.json())
                .then(data => {
                    currentAuctions = {};
                    const grid = document.getElementById('auctionGrid');
                    grid.innerHTML = '';
                    
                    if (data.auctions.length === 0) {
                        grid.innerHTML = '<p>No auctions found</p>';
                        return;
                    }
                    
                    data.auctions.forEach(auction => {
                        currentAuctions[auction.id] = auction;
                        const card = createAuctionCard(auction);
                        grid.appendChild(card);
                        
                        // Join socket room for live updates
                        socket.emit('join_auction', { auction_id: auction.id });
                        
                        // Start timer
                        startAuctionTimer(auction.id);
                    });
                });
        }

        function createAuctionCard(auction) {
            const card = document.createElement('div');
            card.className = 'auction-card';
            card.innerHTML = `
                <img src="${auction.photo1_path || '/static/img/default.jpg'}" class="auction-image">
                <div class="auction-info">
                    <div>
                        <span class="live-badge">🔴 LIVE</span>
                    </div>
                    <div class="crop-name">${auction.crop_name}</div>
                    <div class="auction-details">
                        <strong>Quantity:</strong> ${auction.quantity} quintal<br>
                        <strong>Location:</strong> ${auction.location}<br>
                        <strong>Bidders:</strong> ${auction.bidders_count}
                    </div>
                    <div class="price-section">
                        <div>Base Price (Mandi): <strong>₹${auction.base_price}</strong></div>
                        <div class="current-bid">Current Bid: ₹${auction.current_bid || auction.min_bid}</div>
                        <div class="timer">⏱️ <span id="timer-${auction.id}">--:--:--</span></div>
                    </div>
                    <button class="bid-button" onclick="openBidModal('${auction.id}')">Place Bid</button>
                </div>
            `;
            return card;
        }

        function startAuctionTimer(auctionId) {
            const timerElement = document.getElementById(`timer-${auctionId}`);
            const auction = currentAuctions[auctionId];
            
            setInterval(() => {
                const endTime = new Date(auction.end_time);
                const now = new Date();
                const diff = endTime - now;
                
                if (diff <= 0) {
                    timerElement.textContent = '00:00:00';
                    return;
                }
                
                const hours = Math.floor(diff / 3600000);
                const minutes = Math.floor((diff % 3600000) / 60000);
                const seconds = Math.floor((diff % 60000) / 1000);
                
                timerElement.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            }, 1000);
        }

        // Socket events
        socket.on('bid_placed', (data) => {
            // Update auction in local store
            if (currentAuctions[data.auction.id]) {
                currentAuctions[data.auction.id] = data.auction;
                // Re-render the card
                // ... (update DOM)
            }
            // Show notification
            console.log('New bid placed: ₹' + data.auction.current_bid);
        });

        socket.on('you_were_outbid', (data) => {
            alert(`You were outbid! New bid: ₹${data.amount}`);
        });

        function openBidModal(auctionId) {
            const auction = currentAuctions[auctionId];
            const minBid = (auction.current_bid || auction.min_bid) + 100;
            
            const amount = prompt(`Enter bid amount (minimum ₹${minBid}):`);
            if (amount && parseFloat(amount) >= minBid) {
                placeBid(auctionId, parseFloat(amount));
            }
        }

        function placeBid(auctionId, amount) {
            socket.emit('place_bid', {
                auction_id: auctionId,
                bid_amount: amount
            });
        }

        // Load on page load
        loadAuctions();
        
        // Refresh every 30 seconds
        setInterval(loadAuctions, 30000);
    </script>
</body>
</html>
```

### 4.2 Farmer Dashboard - Create Auction

Create: `templates/create_auction.html`

```html
<!DOCTYPE html>
<html>
<head>
    <title>Create Auction - TelhanSathi</title>
    <style>
        body { font-family: Arial; background: #f5f5f5; padding: 20px; }
        .form-container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
        input, textarea, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; font-family: Arial; }
        textarea { min-height: 100px; resize: vertical; }
        .price-info { background: #e8f8f5; padding: 15px; border-radius: 4px; margin: 15px 0; border-left: 4px solid #2ecc71; }
        .submit-button { width: 100%; padding: 12px; background: #27ae60; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 16px; }
        .submit-button:hover { background: #229954; }
        .photo-upload { margin-top: 10px; }
    </style>
</head>
<body>
    <div class="form-container">
        <h1>🎯 Create Auction</h1>
        
        <form id="auctionForm" onsubmit="submitAuction(event)">
            <!-- Crop Selection -->
            <div class="form-group">
                <label>Crop Name</label>
                <select id="cropName" onchange="updateBasePrice()" required>
                    <option value="">Select Crop</option>
                    <option value="Soybean">Soybean</option>
                    <option value="Mustard">Mustard</option>
                    <option value="Groundnut">Groundnut</option>
                    <option value="Sunflower">Sunflower</option>
                    <option value="Safflower">Safflower</option>
                    <option value="Sesame">Sesame</option>
                    <option value="Coconut">Coconut</option>
                </select>
            </div>

            <!-- Base Price Info -->
            <div class="price-info">
                <strong>📊 Mandi Base Price:</strong> ₹<span id="basePrice">--</span> per quintal
                <br><small>Based on government mandi price data</small>
            </div>

            <!-- Quantity -->
            <div class="form-group">
                <label>Quantity (in quintal)</label>
                <input type="number" id="quantity" min="1" step="0.1" placeholder="e.g., 10" required>
            </div>

            <!-- Minimum Bid Price -->
            <div class="form-group">
                <label>Minimum Bid Price (₹)</label>
                <input type="number" id="minBidPrice" min="0" step="1" placeholder="e.g., 5500" required>
                <small>Buyers must bid at least this amount</small>
            </div>

            <!-- Auction Duration -->
            <div class="form-group">
                <label>Auction Duration</label>
                <select id="duration" required>
                    <option value="6">6 Hours</option>
                    <option value="12">12 Hours</option>
                    <option value="24" selected>24 Hours</option>
                    <option value="48">48 Hours</option>
                </select>
            </div>

            <!-- Location -->
            <div class="form-group">
                <label>Location</label>
                <input type="text" id="location" placeholder="e.g., Indore, MP" required>
            </div>

            <!-- Description -->
            <div class="form-group">
                <label>Description</label>
                <textarea id="description" placeholder="Tell buyers about the quality, harvest date, etc."></textarea>
            </div>

            <!-- Photos -->
            <div class="form-group">
                <label>Photos (up to 3)</label>
                <div class="photo-upload">
                    <input type="file" name="photos" accept="image/*" multiple>
                </div>
            </div>

            <button type="submit" class="submit-button">🚀 Create Auction</button>
        </form>
    </div>

    <script>
        function updateBasePrice() {
            const crop = document.getElementById('cropName').value;
            if (!crop) return;
            
            fetch(`/bidding/get-base-price/${crop}`)
                .then(r => r.json())
                .then(data => {
                    document.getElementById('basePrice').textContent = Math.round(data.base_price);
                    document.getElementById('minBidPrice').placeholder = `e.g., ${Math.round(data.base_price)}`;
                });
        }

        function submitAuction(e) {
            e.preventDefault();
            
            const formData = new FormData();
            formData.append('crop_name', document.getElementById('cropName').value);
            formData.append('quantity', document.getElementById('quantity').value);
            formData.append('min_bid_price', document.getElementById('minBidPrice').value);
            formData.append('duration_hours', document.getElementById('duration').value);
            formData.append('location', document.getElementById('location').value);
            formData.append('description', document.getElementById('description').value);
            
            // Add photos
            const photoInputs = document.querySelector('input[name="photos"]').files;
            for (let photo of photoInputs) {
                formData.append('photos', photo);
            }
            
            fetch('/bidding/farmer/create-auction', {
                method: 'POST',
                body: formData
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert('Auction created successfully! Auction ID: ' + data.auction_id);
                    window.location.href = `/auction/${data.auction_id}`;
                } else {
                    alert('Error: ' + data.message);
                }
            });
        }

        // Load base price on page load
        document.getElementById('cropName').addEventListener('change', updateBasePrice);
    </script>
</body>
</html>
```

---

## 📱 Phase 5: Key Features to Implement

### 5.1 **Auto-Bidding System**

```python
# In websocket_server.py

def process_auto_bids(auction_id):
    """Process auto-bids when new manual bid is placed"""
    auction = Auction.query.get(auction_id)
    auto_bids = Bid.query.filter_by(
        auction_id=auction_id,
        bid_type='auto'
    ).all()
    
    for auto_bid in auto_bids:
        # If auto bidder can outbid
        if auto_bid.max_bid_amount > auction.current_highest_bid:
            # Calculate next bid (current + increment)
            next_bid = min(
                auction.current_highest_bid + auto_bid.auto_increment,
                auto_bid.max_bid_amount
            )
            
            # Place auto bid
            new_bid = Bid(
                auction_id=auction_id,
                buyer_id=auto_bid.buyer_id,
                bid_amount=next_bid,
                bid_type='auto',
                max_bid_amount=auto_bid.max_bid_amount,
                auto_increment=auto_bid.auto_increment,
                is_winning=True
            )
            
            # Update auction
            auction.current_highest_bid = next_bid
            auction.winning_buyer_id = auto_bid.buyer_id
            
            db.session.add(new_bid)
            db.session.commit()
            
            # Notify users
            socketio.emit('bid_placed', {
                'bid': new_bid.to_dict(),
                'auction': auction.to_dict(),
                'auto_placed': True
            }, room=f"auction_{auction_id}")
```

### 5.2 **Auction Auto-End Timer**

```python
# In app.py or separate scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def check_expired_auctions():
    """Check and auto-end expired auctions"""
    expired = Auction.query.filter(
        Auction.status == 'live',
        Auction.end_time <= datetime.utcnow()
    ).all()
    
    for auction in expired:
        winning_bid = Bid.query.filter_by(
            auction_id=auction.id,
            is_winning=True
        ).first()
        
        if winning_bid and winning_bid.bid_amount >= auction.min_bid_price:
            auction.status = 'sold'
            auction.final_price = winning_bid.bid_amount
            
            # Create transaction
            transaction = Transaction(
                auction_id=auction.id,
                seller_id=auction.seller_id,
                buyer_id=winning_bid.buyer_id,
                crop_name=auction.crop_name,
                quantity=auction.quantity_quintal,
                final_price=winning_bid.bid_amount,
                total_amount=auction.quantity_quintal * winning_bid.bid_amount
            )
            db.session.add(transaction)
        else:
            auction.status = 'ended'
        
        db.session.commit()
        
        # Notify participants
        socketio.emit('auction_ended', {
            'auction_id': auction.id,
            'status': auction.status,
            'final_price': auction.final_price
        }, room=f"auction_{auction.id}")

# Schedule to run every minute
scheduler.add_job(check_expired_auctions, 'interval', minutes=1)
scheduler.start()
```

### 5.3 **Notification System**

```python
# Add to models_marketplace.py

class Notification(db.Model):
    __tablename__ = "notifications"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False)  # farmer or buyer id
    user_type = db.Column(db.String(10))  # farmer, buyer
    
    auction_id = db.Column(db.String(36), db.ForeignKey("auctions.id"))
    message = db.Column(db.Text)
    notification_type = db.Column(db.String(50))  # outbid, auction_started, won, etc.
    
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 🚀 Phase 6: Deployment Checklist

- [ ] Create database migrations
- [ ] Set up WebSocket server
- [ ] Implement all API endpoints
- [ ] Create frontend templates
- [ ] Test bidding flow end-to-end
- [ ] Set up auction timer and auto-end
- [ ] Implement notifications
- [ ] Add payment integration
- [ ] Security: Rate limiting on bids
- [ ] Performance: Cache frequent queries
- [ ] Analytics: Track auction metrics
- [ ] Documentation: API docs

---

## 📈 Expected Features

| Feature | Status | Timeline |
|---------|--------|----------|
| Create Auction | ✅ Phase 3 | Week 1 |
| Place Bid | ✅ Phase 3 | Week 1 |
| Auto Bidding | ✅ Phase 5 | Week 2 |
| Live Updates (WebSocket) | ✅ Phase 2 | Week 1 |
| Auction Auto-End | ✅ Phase 5 | Week 2 |
| Notifications | ✅ Phase 5 | Week 2 |
| Payment Integration | ⏳ Phase 6 | Week 3 |
| Dispute Resolution | ⏳ Phase 7 | Week 4 |
| Mobile App | ⏳ Phase 8 | Week 5 |

---

## 💡 Additional Features (Future)

1. **Reserve Price**: Hidden minimum price
2. **Proxy Bidding**: Bid limits
3. **Auction Extensions**: Auto-extend if bids come near end
4. **Seller Feedback**: Ratings after transaction
5. **Wishlist**: Save favorite auctions
6. **Price History**: Compare with past auctions
7. **Bulk Auctions**: Multiple lots at once
8. **Sealed Bid Auctions**: Not reveal bids until end

---

## 🔐 Security Considerations

1. **CSRF Protection**: Use Flask-WTF
2. **SQL Injection**: Use ORM parameterized queries
3. **XSS Prevention**: Escape all user inputs
4. **Rate Limiting**: Limit bids per IP/user
5. **Audit Trail**: Log all bid placements
6. **Fraud Detection**: Monitor unusual bidding patterns

---

## 📊 Analytics & Metrics

- **Auction Success Rate**: (Sold / Total) × 100
- **Average Bid Count**: Total Bids / Total Auctions
- **Price Uplift**: (Final Price - Base Price) / Base Price × 100
- **Bidder Participation**: Unique Bidders / Total Users

---

## 🎓 Testing Strategy

### Unit Tests
- Test bid validation
- Test price calculations
- Test auction status transitions

### Integration Tests
- Test full bidding flow
- Test WebSocket messages
- Test auto-bid logic

### Load Tests
- Concurrent bids on single auction
- Multiple auctions live simultaneously

---

**This comprehensive plan provides everything needed to build a production-grade real-time bidding system for your Mandi Connect platform. Start with Phase 1-3 for MVP, then expand with additional features.**

Would you like me to start implementing any specific phase first?
