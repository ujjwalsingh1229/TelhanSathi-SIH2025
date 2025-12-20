"""
Debug script to check logged-in farmer and their auctions
"""
from app import app, db
from models_marketplace import Auction
from models import Farmer
from flask import session

# Test the farmer ID that has auctions
farmer_with_auctions = 'bbb725c8-3eb0-4a63-9340-442f294ced20'

with app.app_context():
    farmer = Farmer.query.get(farmer_with_auctions)
    if farmer:
        print(f"✅ Farmer found: {farmer.farmer_name if hasattr(farmer, 'farmer_name') else 'Unknown'}")
        print(f"   Farmer ID: {farmer.id}")
        print(f"   Phone/Username: {farmer.phone_number if hasattr(farmer, 'phone_number') else 'N/A'}")
        
        auctions = Auction.query.filter_by(seller_id=farmer_with_auctions).all()
        print(f"\n📊 Auctions created by this farmer: {len(auctions)}")
        
        for i, auction in enumerate(auctions, 1):
            print(f"\n{i}. {auction.crop_name}")
            print(f"   Status: {auction.status}")
            print(f"   Quantity: {auction.quantity_quintal} quintal")
            print(f"   Min Bid: ₹{auction.min_bid_price}")
            print(f"   Created: {auction.created_at}")
    else:
        print("❌ Farmer not found")

print("\n" + "="*50)
print("To see your auctions, make sure you're logged in as the farmer with ID:")
print(f"{farmer_with_auctions}")
print("="*50)
