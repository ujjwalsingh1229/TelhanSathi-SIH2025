#!/usr/bin/env python
"""Test auction creation API endpoint"""

from app import app
from extensions import db
from models import Farmer
import json

def test_create_auction_api():
    """Test the create auction API endpoint"""
    
    # Get a farmer from database
    with app.app_context():
        farmer = Farmer.query.first()
        if not farmer:
            print("ERROR: No farmers found")
            return
        
        farmer_id = farmer.id
        print(f"Using farmer ID: {farmer_id}\n")
    
    # Create test client
    client = app.test_client()
    
    # First, try without authentication (should fail with 401)
    print("=" * 60)
    print("TEST 1: Create auction without authentication")
    print("=" * 60)
    
    form_data = {
        'crop_name': 'Wheat',
        'quantity': '50',
        'min_bid_price': '4500',
        'duration_hours': '24',
        'location': 'Jaipur',
        'description': 'Test auction'
    }
    
    response = client.post(
        '/bidding/farmer/create-auction',
        data=form_data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.get_json()}\n")
    
    # Now test WITH authentication
    print("=" * 60)
    print("TEST 2: Create auction WITH authentication")
    print("=" * 60)
    
    with client.session_transaction() as sess:
        sess['farmer_id_verified'] = farmer_id
        print(f"Session set: farmer_id_verified = {farmer_id}\n")
    
    response = client.post(
        '/bidding/farmer/create-auction',
        data=form_data
    )
    
    print(f"Status Code: {response.status_code}")
    response_json = response.get_json()
    print(f"Response: {json.dumps(response_json, indent=2)}")
    
    if response_json.get('success'):
        print(f"\n✅ Auction created successfully!")
        auction_id = response_json.get('auction_id')
        print(f"   Auction ID: {auction_id}")
    else:
        print(f"\n❌ Failed to create auction")
        print(f"   Error: {response_json.get('error')}")

if __name__ == '__main__':
    test_create_auction_api()
