import uuid
from datetime import datetime
from extensions import db


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

    offers = db.relationship(
        "BuyerOffer",
        backref="listing",
        lazy=True,
        cascade="all, delete-orphan"
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
    listing_id = db.Column(db.String(36), db.ForeignKey("crop_listings.id"), nullable=False)

    buyer_name = db.Column(db.String(255))
    buyer_mobile = db.Column(db.String(20))
    buyer_location = db.Column(db.String(255))

    initial_price = db.Column(db.Float)
    final_price = db.Column(db.Float, nullable=True)

    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MarketPrice(db.Model):
    __tablename__ = "market_prices"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    crop_name = db.Column(db.String(100), nullable=False)
    buyer_name = db.Column(db.String(255))
    distance_km = db.Column(db.Float)
    price = db.Column(db.Float)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


