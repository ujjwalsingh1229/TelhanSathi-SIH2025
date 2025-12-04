from extensions import db
from datetime import datetime
import uuid

class Farmer(db.Model):
    """
    Farmer model based on Maharashtra AgriStack and MahaDBT portal schema.
    Stores comprehensive farmer profile including personal, address, land, and financial details.
    """
    __tablename__ = 'farmers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # ===== PERSONAL & DEMOGRAPHIC INFORMATION =====
    # Kisan Pehchan Patra (12-digit ID) - Unique identifier
    farmer_id = db.Column(db.String(12), unique=True, nullable=False, index=True)
    
    # Name
    name = db.Column(db.String(255), nullable=False)
    
    # Aadhaar Number (12-digit, linked to identity verification)
    aadhaar_number = db.Column(db.String(12), unique=True)
    
    # Date of Birth
    date_of_birth = db.Column(db.Date)
    
    # Gender (M/F/Other)
    gender = db.Column(db.String(10))
    
    # Contact Information
    phone_number = db.Column(db.String(10), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255))
    
    # Caste Category (General/OBC/SC/ST)
    caste_category = db.Column(db.String(50))
    caste_certificate_path = db.Column(db.String(255))  # Path to uploaded certificate
    
    # Physically Handicapped Status (Yes/No)
    is_physically_handicapped = db.Column(db.Boolean, default=False)
    disability_certificate_path = db.Column(db.String(255))
    
    # Domicile Status (Maharashtra resident verification)
    is_maharashtra_resident = db.Column(db.Boolean, default=True)
    
    # ===== ADDRESS INFORMATION =====
    # Permanent Address
    permanent_address = db.Column(db.String(500))
    
    # Location Details
    district = db.Column(db.String(100), nullable=False)
    taluka = db.Column(db.String(100))
    village = db.Column(db.String(100))
    state = db.Column(db.String(100), default='Maharashtra')
    
    pincode = db.Column(db.String(6))
    
    # GPS Coordinates (for location-based services)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # ===== LAND OWNERSHIP & AGRICULTURAL DETAILS =====
    # Land Records Information
    # 7/12 Extract (Record of Rights) - Path to document
    record_of_rights_7_12_path = db.Column(db.String(255))
    
    # 8A Document (Lease deed) - Path to document
    lease_deed_8a_path = db.Column(db.String(255))
    
    # Land Survey Numbers (comma-separated if multiple)
    land_survey_numbers = db.Column(db.String(500))
    
    # Total Land Area in hectares
    total_land_area_hectares = db.Column(db.Float, nullable=False, default=0.0)
    
    # Land Area in Gunthas (traditional Maharashtrian measurement: 1 guntha ≈ 0.025 hectare)
    land_area_gunthas = db.Column(db.Float, default=0.0)
    
    # Land Holder Type (Owner/Co-owner/Tenant/Sharecropper)
    land_holder_type = db.Column(db.String(50), default='Owner')
    
    # Indicates if farmer owns land in multiple villages
    owns_land_in_multiple_villages = db.Column(db.Boolean, default=False)
    
    # Soil Type (Loamy, Clay, Sandy, Black Soil, Red Soil, etc.)
    soil_type = db.Column(db.String(100))
    
    # Current Crop(s) cultivated (stored as comma-separated or JSON)
    current_crops = db.Column(db.String(500))
    
    # Oilseed Farmer Status (enrolled in oilseed cultivation scheme)
    is_oilseed_farmer = db.Column(db.Boolean, default=False)
    oilseed_enrollment_date = db.Column(db.DateTime)
    
    # ===== FINANCIAL INFORMATION =====
    # Bank Account Details
    bank_name = db.Column(db.String(100))
    bank_branch = db.Column(db.String(100))
    account_number = db.Column(db.String(20))
    account_holder_name = db.Column(db.String(255))
    ifsc_code = db.Column(db.String(11))  # IFSC code format: 4 letters + 0 + 6 digits
    
    # Income Certificate Details (if applicable)
    income_certificate_path = db.Column(db.String(255))
    annual_income = db.Column(db.Float)
    
    # PM-KISAN Beneficiary Status
    is_pm_kisan_beneficiary = db.Column(db.Boolean, default=False)
    pm_kisan_reference_id = db.Column(db.String(100))
    
    # ===== ACCOUNT STATUS & VERIFICATION =====
    is_verified = db.Column(db.Boolean, default=False)
    verification_timestamp = db.Column(db.DateTime)
    
    # Document verification status
    documents_verified = db.Column(db.Boolean, default=False)

    # Has the farmer completed the onboarding flow (UI-driven quick profile)?
    # Soil Type (Loamy, Clay, Sandy, Black Soil, Red Soil, etc.)
    soil_type = db.Column(db.String(100))

    # Water Type (Freshwater, Salt Water, Brackish Water)
    water_type = db.Column(db.String(50))

    # Irrigation Type (Tube Well, Well, Rainfed, Canal)
    # irrigation_type = db.Column(db.String(50))

    # Harvest Date (YYYY-MM)
    harvest_date = db.Column(db.Date)

    # Selected unit for land size (acre / hectare / bigha)
    land_unit = db.Column(db.String(20), default="acre")

    # Current Crop(s) cultivated (stored as comma-separated or JSON)
    current_crops = db.Column(db.String(500))
    onboarding_completed = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ===== RELATIONSHIPS =====
    otp_records = db.relationship('OTPRecord', backref='farmer', lazy=True, cascade='all, delete-orphan')
    subsidy_applications = db.relationship('SubsidyApplication', backref='farmer', lazy=True, cascade='all, delete-orphan')
    price_alerts = db.relationship('PriceAlert', backref='farmer', lazy=True, cascade='all, delete-orphan')
    rewards = db.relationship('FarmerReward', backref='farmer', lazy=True, cascade='all, delete-orphan')


    
    def __repr__(self):
        return f'<Farmer {self.farmer_id} - {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'name': self.name,
            'aadhaar_number': self.aadhaar_number,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'phone': self.phone_number,
            'email': self.email,
            'district': self.district,
            'taluka': self.taluka,
            'village': self.village,
            'state': self.state,
            'pincode': self.pincode,
            'total_land_area_hectares': self.total_land_area_hectares,
            'land_area_gunthas': self.land_area_gunthas,
            'land_type': self.land_holder_type,
            'soil_type': self.soil_type,
            'current_crops': self.current_crops,
            'water_type': self.water_type,
            'bank_name': self.bank_name,
            'bank_account_number': self.account_number,
            'ifsc_code': self.ifsc_code,
            'aadhar_number': self.aadhaar_number,
            'is_verified': self.is_verified,
            'documents_verified': self.documents_verified,
            'photo_url': None,
            'land_unit': self.land_unit,
            'harvest_date': self.harvest_date.isoformat() if self.harvest_date else None,
        }



class OTPRecord(db.Model):
    """
    OTP authentication records for Farmer ID-based login.
    Stores OTP, expiry, and verification status.
    """
    __tablename__ = 'otp_records'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = db.Column(db.String(36), db.ForeignKey('farmers.id'), nullable=False)
    
    otp_code = db.Column(db.String(6), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    verified_at = db.Column(db.DateTime)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f'<OTP {self.otp_code} for Farmer {self.farmer_id}>'


class Scheme(db.Model):
    r"""
    Master list of government schemes and subsidies.
        cd "C:\Users\dhira\OneDrive\Desktop\dhirudurgade github\TelhanSathi-SIH2025\backend"
    flask db migrate -m "Add Scheme and SubsidyApplication models"
    flask db upgrades all available subsidies/schemes data.
    """
    __tablename__ = 'schemes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Scheme Identifier
    scheme_code = db.Column(db.String(50), unique=True, nullable=False, index=True)  # e.g., 'pmkisan', 'nmeo'
    
    # Basic Information
    name = db.Column(db.String(255), nullable=False)  # PM-KISAN Samman Nidhi
    description = db.Column(db.Text, nullable=False)  # Full description
    
    # Category/Type
    scheme_type = db.Column(db.String(50), nullable=False)  # 'subsidy' or 'scheme'
    focus_area = db.Column(db.String(100), nullable=False)  # Income Support, Crop Switch, Equipment, etc.
    focus_color = db.Column(db.String(20), default="#2196f3")  # Color code for UI
    
    # Benefit Details
    benefit_amount = db.Column(db.String(255), nullable=False)  # ₹6,000/year, 40-50% Subsidy, etc.
    eligibility_criteria = db.Column(db.Text, nullable=False)  # Eligibility requirements
    
    # How to Apply (stored as JSON list of steps)
    apply_steps = db.Column(db.Text)  # JSON array of application steps
    
    # External Link for more info or direct application
    external_link = db.Column(db.String(255))
    
    # Recommendation Flag (for "Recommended for You" filter)
    is_recommended = db.Column(db.Boolean, default=False)
    
    # Active Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Required Documents (stored as JSON list)
    required_documents = db.Column(db.Text)  # JSON array of required documents
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subsidy_applications = db.relationship('SubsidyApplication', backref='scheme', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Scheme {self.name}>'
    
    def to_dict(self):
        """Convert scheme to dictionary for JSON response."""
        import json
        return {
            'id': self.id,
            'scheme_code': self.scheme_code,
            'name': self.name,
            'description': self.description,
            'scheme_type': self.scheme_type,
            'focus_area': self.focus_area,
            'focus_color': self.focus_color,
            'benefit_amount': self.benefit_amount,
            'eligibility_criteria': self.eligibility_criteria,
            'apply_steps': json.loads(self.apply_steps) if self.apply_steps else [],
            'external_link': self.external_link,
            'is_recommended': self.is_recommended,
            'is_active': self.is_active,
            'required_documents': json.loads(self.required_documents) if self.required_documents else [],
            'created_at': self.created_at.isoformat()
        }


class SubsidyApplication(db.Model):
    """
    Tracks farmer applications for specific schemes/subsidies.
    """
    __tablename__ = 'subsidy_applications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = db.Column(db.String(36), db.ForeignKey('farmers.id'), nullable=False)
    scheme_id = db.Column(db.String(36), db.ForeignKey('schemes.id'), nullable=False)
    
    # Application Details
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status: Applied, Verified, Approved, Disbursed, Rejected
    status = db.Column(db.String(50), default='Applied')
    
    # Subsidy/Scheme Specific Data (JSON for flexibility)
    application_data = db.Column(db.Text)  # JSON: crop, quantity, location, etc.
    
    # Approval Details
    approved_amount = db.Column(db.Float)
    approval_date = db.Column(db.DateTime)
    
    # Generated PDF path (auto-filled application)
    application_pdf_path = db.Column(db.String(255))
    
    # Notes from admin
    admin_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SubsidyApplication {self.scheme_id} - {self.status}>'


class PriceAlert(db.Model):
    """
    Price alerts for oilseed commodities.
    Stores alert preferences and notification history.
    """
    __tablename__ = 'price_alerts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = db.Column(db.String(36), db.ForeignKey('farmers.id'), nullable=False)
    
    # Commodity: Mustard, Groundnut, Soybean, etc.
    commodity = db.Column(db.String(100), nullable=False)
    
    # Target Market/Mandi
    mandi_name = db.Column(db.String(100))
    
    # Alert Threshold (price in ₹/quintal)
    alert_price = db.Column(db.Float, nullable=False)
    alert_type = db.Column(db.String(20))  # 'above' or 'below'
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PriceAlert {self.commodity} @ {self.mandi_name}>'


class FarmerReward(db.Model):
    """
    Gamification - Rewards and points system.
    """
    __tablename__ = 'farmer_rewards'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = db.Column(db.String(36), db.ForeignKey('farmers.id'), nullable=False)
    
    total_points = db.Column(db.Float, default=0)
    
    # Point breakdown
    points_from_switching = db.Column(db.Float, default=0)  # 500 pts
    points_from_soil_test = db.Column(db.Float, default=0)  # 100 pts
    points_from_sales = db.Column(db.Float, default=0)  # 200 pts
    
    rank = db.Column(db.Integer)  # Village/District leaderboard rank
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FarmerReward Points: {self.total_points}>'


class Notification(db.Model):
    r"""
    Notifications for farmers - alerts, updates, important messages.
    Types: scheme_update, deal_alert, price_alert, general_alert, system_update
    """
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = db.Column(db.String(36), db.ForeignKey('farmers.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # scheme_update, deal_alert, price_alert, general_alert, system_update
    icon = db.Column(db.String(50), nullable=True)  # Icon name for frontend display
    color = db.Column(db.String(20), nullable=True)  # Color code (success, warning, info, error)
    related_id = db.Column(db.String(36), nullable=True)  # Links to scheme/deal/crop if applicable
    related_type = db.Column(db.String(50), nullable=True)  # scheme, deal, crop, general
    action_link = db.Column(db.String(255), nullable=True)  # URL to navigate to
    is_read = db.Column(db.Boolean, default=False)
    is_important = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=True)  # Auto-expire old notifications
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.title} for Farmer {self.farmer_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.notification_type,
            'icon': self.icon,
            'color': self.color,
            'relatedId': self.related_id,
            'relatedType': self.related_type,
            'actionLink': self.action_link,
            'isRead': self.is_read,
            'isImportant': self.is_important,
            'expiresAt': self.expires_at.isoformat() if self.expires_at else None,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }


class DeviceRequest(db.Model):
    """Records farmer requests for an IoT kit installation."""
    __tablename__ = 'device_requests'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = db.Column(db.String(36), db.ForeignKey('farmers.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected, scheduled
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<DeviceRequest {self.id} for Farmer {self.farmer_id}>'


class IoTDevice(db.Model):
    """Represents an installed IoT kit (ESP32 + sensors) for a farmer."""
    __tablename__ = 'iot_devices'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = db.Column(db.String(36), db.ForeignKey('farmers.id'), nullable=False)
    device_serial = db.Column(db.String(100), unique=True)
    installed = db.Column(db.Boolean, default=False)
    installed_at = db.Column(db.DateTime)
    location_description = db.Column(db.String(255))

    def __repr__(self):
        return f'<IoTDevice {self.device_serial} farmer:{self.farmer_id}>'


class SensorReading(db.Model):
    """Stores sensor readings pushed from the IoT kit."""
    __tablename__ = 'sensor_readings'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = db.Column(db.String(36), db.ForeignKey('iot_devices.id'), nullable=False)
    temperature = db.Column(db.Float)  # ambient
    humidity = db.Column(db.Float)
    soil_moisture = db.Column(db.Float)
    light = db.Column(db.Float)
    probe_temp = db.Column(db.Float)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SensorReading {self.id} device:{self.device_id} at {self.received_at}>'

