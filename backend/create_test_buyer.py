from app import app, db
from models_marketplace import Buyer
from werkzeug.security import generate_password_hash
import uuid

with app.app_context():
    # Check if test buyer exists
    test_buyer = Buyer.query.filter_by(email='testbuyer@example.com').first()
    if test_buyer:
        print(f'Test buyer already exists: {test_buyer.id}')
    else:
        # Create test buyer
        new_buyer = Buyer(
            id=str(uuid.uuid4()),
            email='testbuyer@example.com',
            password=generate_password_hash('password123'),
            buyer_name='Test Buyer',
            phone='9876543210',
            company_name='Test Company',
            location='Jaipur',
            district='Jaipur',
            is_verified=True,
            is_active=True
        )
        db.session.add(new_buyer)
        db.session.commit()
        print(f'Created test buyer: {new_buyer.id}')
        print(f'Email: testbuyer@example.com')
        print(f'Password: password123')
