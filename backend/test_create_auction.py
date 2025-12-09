#!/usr/bin/env python
"""Simulate auction creation request"""

from app import app
from extensions import db
from models_marketplace import Auction
from models import Farmer
from datetime import datetime, timedelta
import uuid

# Test creating an auction directly in the database
with app.app_context():
    # Get a farmer
    farmer = Farmer.query.first()
    if not farmer:
        print("ERROR: No farmers found in database")
        exit(1)
    
    print(f"Using farmer: {farmer.id} ({farmer.name if hasattr(farmer, 'name') else 'N/A'})")
    
    # Try to create an auction
    try:
        new_auction = Auction(
            seller_id=farmer.id,
            crop_name="Wheat",
            quantity_quintal=50.0,
            base_price=5000.0,
            min_bid_price=4500.0,
            end_time=datetime.utcnow() + timedelta(hours=24),
            location="Jaipur",
            description="Test auction"
        )
        
        db.session.add(new_auction)
        db.session.commit()
        
        print(f"\n✅ Auction created successfully!")
        print(f"   Auction ID: {new_auction.id}")
        print(f"   Crop: {new_auction.crop_name}")
        print(f"   Quantity: {new_auction.quantity_quintal} quintals")
        print(f"   Base Price: ₹{new_auction.base_price}")
        print(f"   Min Bid: ₹{new_auction.min_bid_price}")
        print(f"   Status: {new_auction.status}")
        print(f"   End Time: {new_auction.end_time}")
        
        # Verify it was saved
        saved = Auction.query.get(new_auction.id)
        if saved:
            print(f"\n✅ Auction verified in database!")
        else:
            print(f"\n❌ Auction NOT found in database after commit!")
            
    except Exception as e:
        print(f"❌ Error creating auction: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
