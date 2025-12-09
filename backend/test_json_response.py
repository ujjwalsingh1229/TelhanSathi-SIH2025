"""
Test API responses for auctions
"""
from app import app, db
from models_marketplace import Auction
from models import Farmer
import json

with app.app_context():
    farmer_id = 'bbb725c8-3eb0-4a63-9340-442f294ced20'
    auctions = Auction.query.filter_by(seller_id=farmer_id).all()
    
    print(f'Testing API endpoint response:')
    print(f'Total auctions: {len(auctions)}')
    
    # Test the to_dict conversion
    auction_dicts = [a.to_dict() for a in auctions]
    
    # Check if it's serializable
    try:
        json_str = json.dumps(auction_dicts, default=str)
        print(f'✅ JSON serialization works')
        print(f'First auction: {auction_dicts[0]["crop_name"]} - {auction_dicts[0]["status"]}')
        print(f'Bids count: {auction_dicts[0]["bids_count"]}')
        print(f'Bidders count: {auction_dicts[0]["bidders_count"]}')
    except Exception as e:
        print(f'❌ JSON serialization error: {e}')
