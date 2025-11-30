import sys
from datetime import datetime
from app import app, db
from models import Farmer, OTPRecord, SubsidyApplication, PriceAlert, FarmerReward

# Create application context
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")
    
    # Seed sample farmer data for testing
    if Farmer.query.count() < 20:
        sample_farmer = Farmer(
            farmer_id="567894251679",
            name="Gopal Durgade",
            aadhaar_number="241632683721",
            date_of_birth=datetime.strptime("1980-05-15", "%Y-%m-%d").date(),
            gender="M",
            phone_number="+918805937758",
            email="ramesh@example.com",
            caste_category="OBC",
            is_physically_handicapped=False,
            is_maharashtra_resident=True,
            permanent_address="Gauri Shankar park, Miraj",
            district="Sangli",
            taluka="Miraj",
            village="Miraj",
            state="Maharashtra",
            pincode="416410",
            latitude=27.2232,
            longitude=77.4470,
            land_survey_numbers="12/A, 13/B",
            total_land_area_hectares=2.5,
            land_area_gunthas=100,
            land_holder_type="Owner",
            soil_type="Loamy",
            current_crops="Paddy, Wheat",
            bank_name="Bank of Baroda",
            bank_branch="Miraj Branch",
            account_number="1234567890",
            account_holder_name="Dhiraj Durgade",
            ifsc_code="SBIN0001234",
            is_pm_kisan_beneficiary=True,
            pm_kisan_reference_id="PM-KISAN-12345",
            is_verified=True,
            verification_timestamp=datetime.utcnow(),
            documents_verified=True
        )
        db.session.add(sample_farmer)
        db.session.commit()
        print("✅ Sample farmer seeded with complete AgriStack data!")
    else:
        print("📊 Database already has data.")
