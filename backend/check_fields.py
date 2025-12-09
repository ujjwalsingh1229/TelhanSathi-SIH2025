#!/usr/bin/env python3
"""Check exact field names and values from auctions"""

from models_marketplace import Auction
from extensions import db
import app as app_module
import json

# Get the Flask app instance
flask_app = app_module.app

with flask_app.app_context():
    auction = Auction.query.first()
    
    if auction:
        print("=" * 60)
        print("AUCTION MODEL FIELDS:")
        print("=" * 60)
        
        # Print database columns
        print("\nDatabase Columns:")
        for col in Auction.__table__.columns:
            value = getattr(auction, col.name)
            print(f"  {col.name:25} = {value}")
        
        print("\n" + "=" * 60)
        print("to_dict() OUTPUT FIELDS:")
        print("=" * 60)
        
        auction_dict = auction.to_dict()
        for key, value in sorted(auction_dict.items()):
            value_type = type(value).__name__
            print(f"  {key:25} ({value_type:10}) = {value}")
        
        print("\n" + "=" * 60)
        print("FIELD MAPPING CHECK:")
        print("=" * 60)
        
        # Check which fields the HTML expects
        print("\nFields used in my_auctions.html:")
        expected_fields = [
            'crop_name', 'quantity', 'base_price', 'min_bid', 'current_bid',
            'bids_count', 'bidders_count', 'avg_bid', 'location', 
            'start_time', 'end_time', 'status', 'final_price'
        ]
        
        for field in expected_fields:
            if field in auction_dict:
                print(f"  ✅ {field:25} = {auction_dict[field]}")
            else:
                print(f"  ❌ {field:25} = MISSING")
        
        print("\n" + "=" * 60)
        print("JSON SERIALIZATION TEST:")
        print("=" * 60)
        try:
            json_str = json.dumps(auction_dict)
            print(f"  ✅ Successfully serialized to JSON ({len(json_str)} bytes)")
        except Exception as e:
            print(f"  ❌ Serialization failed: {e}")
    else:
        print("No auctions found in database")
