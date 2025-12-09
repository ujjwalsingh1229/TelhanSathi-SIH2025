#!/usr/bin/env python
"""Test auction creation issue"""

from app import app
from extensions import db
from models_marketplace import Auction
from models import Farmer
from datetime import datetime, timedelta

with app.app_context():
    # Check if table exists
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tables in database: {len(tables)} tables found")
    print(f"'auctions' table exists: {'auctions' in tables}")
    
    if 'auctions' in tables:
        columns = [col['name'] for col in inspector.get_columns('auctions')]
        print(f"\nAuction table columns ({len(columns)}):")
        for col in columns:
            print(f"  - {col}")
        
        # Try to count existing auctions
        auction_count = Auction.query.count()
        print(f"\nTotal auctions in database: {auction_count}")
        
        # Get sample farmers
        farmers = Farmer.query.limit(5).all()
        print(f"\nSample farmers ({len(farmers)}):")
        for farmer in farmers:
            print(f"  - ID: {farmer.id}, Name: {farmer.name if hasattr(farmer, 'name') else 'N/A'}")
