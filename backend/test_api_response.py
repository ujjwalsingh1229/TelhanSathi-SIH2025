#!/usr/bin/env python3
"""Test the actual API response"""

from models_marketplace import Auction
from models import Farmer
from extensions import db
import app as app_module
import json

flask_app = app_module.app

with flask_app.app_context():
    # Check farmer data
    farmers = Farmer.query.limit(3).all()
    print("=" * 70)
    print("FARMERS IN DATABASE:")
    print("=" * 70)
    for farmer in farmers:
        auctions_count = Auction.query.filter_by(seller_id=farmer.id).count()
        print(f"\nFarmer ID: {farmer.id}")
        print(f"  Phone: {farmer.phone_number}")
        print(f"  Name: {farmer.name}")
        print(f"  Auctions created: {auctions_count}")
        if auctions_count > 0:
            for auction in Auction.query.filter_by(seller_id=farmer.id).limit(2).all():
                print(f"    - {auction.crop_name} ({auction.status})")
    
    print("\n" + "=" * 70)
    print("TOTAL AUCTIONS IN DATABASE:")
    print("=" * 70)
    total = Auction.query.count()
    print(f"Total auctions: {total}")
    
    # Get all auctions and their seller IDs
    all_auctions = Auction.query.all()
    print(f"\nAll auction sellers:")
    seller_dict = {}
    for auction in all_auctions:
        if auction.seller_id not in seller_dict:
            seller_dict[auction.seller_id] = 0
        seller_dict[auction.seller_id] += 1
    
    for seller_id, count in seller_dict.items():
        farmer = Farmer.query.get(seller_id)
        farmer_name = farmer.name if farmer else "UNKNOWN"
        print(f"  {seller_id}: {count} auctions (Farmer: {farmer_name})")

    print("\n" + "=" * 70)
    print("SIMULATING FARMER_AUCTIONS() FUNCTION:")
    print("=" * 70)
    
    # Test what farmer_auctions() would return for each farmer
    for farmer_id, count in seller_dict.items():
        farmer = Farmer.query.get(farmer_id)
        farmer_phone = farmer.phone_number if farmer else "UNKNOWN"
        
        # This is what farmer_auctions() does
        query = Auction.query.filter_by(seller_id=farmer_id)
        auctions = query.all()
        
        print(f"\nFarmer: {farmer_phone} (ID: {farmer_id})")
        print(f"  Query result: {len(auctions)} auctions")
        
        # Simulate the response
        response = {
            'auctions': [auction.to_dict() for auction in auctions],
            'total': len(auctions),
            'filters': {'status': 'all', 'sort': 'newest'}
        }
        
        print(f"  Response total: {response['total']}")
        print(f"  First auction: {response['auctions'][0]['crop_name'] if response['auctions'] else 'N/A'}")
