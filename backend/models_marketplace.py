import uuid
from datetime import datetime
from extensions import db


class Buyer(db.Model):
    """Buyer model for marketplace - stores buyer profile and credentials"""
    __tablename__ = "buyers"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Login credentials
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    
    # Profile information
    buyer_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    company_name = db.Column(db.String(255))
    
    # Location information
    location = db.Column(db.String(255))
    district = db.Column(db.String(100))
    state = db.Column(db.String(100), default='Maharashtra')
    
    # Account status
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    buyer_offers = db.relationship('BuyerOffer', backref='buyer', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Buyer {self.buyer_name} - {self.email}>'


class CropListing(db.Model):
    __tablename__ = "crop_listings"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = db.Column(db.String(36), db.ForeignKey("farmers.id"), nullable=False)

    crop_name = db.Column(db.String(100), nullable=False)
    quantity_quintal = db.Column(db.Float, nullable=False)
    expected_price = db.Column(db.Float, nullable=False)
    harvest_date = db.Column(db.Date)

    # Photos
    photo1_path = db.Column(db.String(255))
    photo2_path = db.Column(db.String(255))
    photo3_path = db.Column(db.String(255))

    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class SellRequest(db.Model):
    __tablename__ = "sell_requests"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = db.Column(db.String(36), db.ForeignKey("farmers.id"), nullable=False)

    crop_name = db.Column(db.String(100), nullable=False)
    quantity_quintal = db.Column(db.Float, nullable=False)
    expected_price = db.Column(db.Float, nullable=False)

    harvest_date = db.Column(db.String(20))
    location = db.Column(db.String(255))
    farmer_name = db.Column(db.String(200))
    farmer_phone = db.Column(db.String(20))

    status = db.Column(db.String(20), default="pending")  
    # pending → accepted → final_confirmed → declined

    # buyer negotiation
    buyer_price = db.Column(db.Float)
    final_price = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    photos = db.relationship("SellPhoto", backref="sell_request", cascade="all,delete")


class SellPhoto(db.Model):
    __tablename__ = "sell_photos"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = db.Column(db.String(36), db.ForeignKey("sell_requests.id"))
    photo_url = db.Column(db.String(255), nullable=False)


class BuyerOffer(db.Model):
    __tablename__ = "buyer_offers"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Buyer information (FK to Buyer table)
    buyer_id = db.Column(db.String(36), db.ForeignKey("buyers.id"), nullable=True)
    buyer_name = db.Column(db.String(255))
    buyer_mobile = db.Column(db.String(20))
    buyer_location = db.Column(db.String(255))
    buyer_company = db.Column(db.String(255))
    
    # Crop details (buyer specifies what they want to buy)
    crop_name = db.Column(db.String(100), nullable=False)
    quantity_quintal = db.Column(db.Float, nullable=False)
    location_wanted = db.Column(db.String(255))  # Where buyer wants crop from
    district_wanted = db.Column(db.String(100))
    
    # Pricing
    initial_price = db.Column(db.Float, nullable=False)  # Buyer's offer price
    final_price = db.Column(db.Float, nullable=True)     # Negotiated final price
    
    # Optional: Reference to farmer's SellRequest if farmer responds
    sell_request_id = db.Column(db.String(36), db.ForeignKey("sell_requests.id"), nullable=True)
    
    # Status: pending → accepted (by farmer) → final_confirmed → declined
    status = db.Column(db.String(20), default="pending")
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BuyerOffer {self.crop_name} by {self.buyer_name}>'


class MarketPrice(db.Model):
    __tablename__ = "market_prices"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    crop_name = db.Column(db.String(100), nullable=False)
    buyer_name = db.Column(db.String(255))
    distance_km = db.Column(db.Float)
    price = db.Column(db.Float)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


