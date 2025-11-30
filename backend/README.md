# Telhan Sathi - Backend (Flask)

**Digital Platform for Oilseed Cultivation Decision Support**

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
Create a `.env` file in the backend folder with your configuration (see `.env.example`).

### 3. Initialize Database
```bash
python setup_db.py
```

### 4. Run Flask Server
```bash
python app.py
```

Server runs on `http://localhost:5000`

---

## 📋 API Endpoints

### Authentication (Farmer ID + OTP)

#### 1. **Register Farmer**
- **Endpoint:** `POST /api/auth/register`
- **Description:** Register a new farmer with Kisan Pehchan Patra
- **Request Body:**
```json
{
  "farmer_id": "123456789012",
  "name": "Ramesh Kumar",
  "phone_number": "9876543210",
  "email": "ramesh@example.com",
  "land_size_hectares": 2.5,
  "district": "Bharatpur",
  "state": "Rajasthan",
  "village": "Bayana",
  "soil_type": "Loamy",
  "current_crop": "Paddy",
  "latitude": 27.2232,
  "longitude": 77.4470
}
```

#### 2. **Request OTP** (Step 1 of Login)
- **Endpoint:** `POST /api/auth/request-otp`
- **Description:** Send OTP to farmer's registered phone
- **Request Body:**
```json
{
  "farmer_id": "123456789012"
}
```

#### 3. **Verify OTP** (Step 2 of Login)
- **Endpoint:** `POST /api/auth/verify-otp`
- **Description:** Verify OTP and login farmer
- **Request Body:**
```json
{
  "farmer_id": "123456789012",
  "otp_code": "123456"
}
```
- **Response:** Returns farmer profile + subsidy eligibility

#### 4. **Get Farmer Profile**
- **Endpoint:** `GET /api/auth/farmer/<farmer_id>`
- **Description:** Fetch farmer details by Kisan Patra ID

---

## 🗄️ Database Models

### Farmer
- `farmer_id` (Kisan Pehchan Patra - 12 digit)
- `name`, `phone_number`, `email`
- `land_size_hectares`, `district`, `state`
- `soil_type`, `current_crop`
- `latitude`, `longitude`
- `is_verified`, `created_at`, `updated_at`

### OTPRecord
- Links OTP codes to farmers
- `otp_code`, `is_verified`, `expires_at`

### SubsidyApplication
- Tracks subsidy applications
- `crop`, `status` (Applied/Verified/Disbursed)
- `subsidy_amount`, `application_pdf_path`

### PriceAlert
- Price alerts for commodities
- `commodity`, `mandi_name`, `alert_price`

### FarmerReward
- Gamification rewards
- `total_points`, `rank`

---

## 🔧 Configuration

**`.env` file variables:**
- `FLASK_ENV`: development/production
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: SQLite or PostgreSQL URL
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`: For SMS OTP
- `OTP_EXPIRY_SECONDS`: OTP validity duration

---

## 📱 Workflow

1. **Farmer Registration** → Enter Kisan Pehchan Patra details
2. **Request OTP** → Farmer enters Kisan Patra ID
3. **Verify OTP** → Farmer enters received OTP
4. **Login Successful** → App loads farmer profile + auto-filled subsidies

---

## 🎯 Modules (Coming Next)

- [ ] Fayda Calculator (Profit Simulator)
- [ ] Mandi Connect (Price Alerts + Digital Assurance)
- [ ] One-Click Sahayata (Auto Subsidy Application)
- [ ] Khet Nighrani (IoT Sensors + Weather)
- [ ] Kisan Rewards (Gamification)
- [ ] X-Factor Features (Voice, Disease Detection, etc.)

---

## 👥 Team Allocation

**Dhiraj (Backend):** All API endpoints, database logic, integrations
