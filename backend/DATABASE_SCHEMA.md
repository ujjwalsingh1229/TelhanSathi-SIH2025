# Database Schema Reference

## Tables Used in Market Deal Flow

### 1. sell_requests Table
Stores all sell requests created by farmers.

```sql
CREATE TABLE sell_requests (
    id VARCHAR(36) PRIMARY KEY,
    farmer_id VARCHAR(36) NOT NULL FOREIGN KEY -> farmers.id,
    
    -- Crop Information
    crop_name VARCHAR(100) NOT NULL,
    quantity_quintal FLOAT NOT NULL,
    expected_price FLOAT NOT NULL,
    harvest_date VARCHAR(20),
    
    -- Location Information
    location VARCHAR(255),
    farmer_name VARCHAR(200),
    farmer_phone VARCHAR(20),
    
    -- Deal Status
    status VARCHAR(20) DEFAULT 'pending',
    -- Values: 'pending', 'accepted', 'declined', 'final_confirmed'
    
    -- Pricing
    buyer_price FLOAT,
    final_price FLOAT,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Sample Data:
```sql
INSERT INTO sell_requests VALUES (
    'sell-001',
    'farmer-001',
    'Mustard',
    50,
    5450,
    '2025-03-15',
    'Village Khera, Bharatpur',
    'Ramesh Kumar',
    '+91 9876543210',
    'pending',
    NULL,
    NULL,
    '2025-12-03 10:30:00',
    '2025-12-03 10:30:00'
);
```

---

### 2. sell_photos Table
Stores photo uploads associated with sell requests.

```sql
CREATE TABLE sell_photos (
    id VARCHAR(36) PRIMARY KEY,
    request_id VARCHAR(36) NOT NULL FOREIGN KEY -> sell_requests.id,
    photo_url VARCHAR(255) NOT NULL,
    -- Example: 'static/uploads/550e8400-e29b-41d4-a716-446655440000_crop.jpg'
);
```

#### Sample Data:
```sql
INSERT INTO sell_photos VALUES (
    'photo-001',
    'sell-001',
    'static/uploads/550e8400-e29b-41d4-a716-446655440000_photo1.jpg'
);

INSERT INTO sell_photos VALUES (
    'photo-002',
    'sell-001',
    'static/uploads/550e8400-e29b-41d4-a716-446655440001_photo2.jpg'
);

INSERT INTO sell_photos VALUES (
    'photo-003',
    'sell-001',
    'static/uploads/550e8400-e29b-41d4-a716-446655440002_photo3.jpg'
);
```

---

### 3. farmers Table
Existing table, used for farmer information.

```sql
CREATE TABLE farmers (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    phone_number VARCHAR(20),
    village VARCHAR(100),
    district VARCHAR(100),
    state VARCHAR(100),
    -- ... other fields
);
```

---

### 4. market_prices Table
Stores market prices for different crops/buyers.

```sql
CREATE TABLE market_prices (
    id VARCHAR(36) PRIMARY KEY,
    crop_name VARCHAR(100) NOT NULL,
    buyer_name VARCHAR(255),
    distance_km FLOAT,
    price FLOAT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### Sample Data (Fallback):
```sql
INSERT INTO market_prices VALUES 
    ('m1', 'Mustard', 'Bharatpur Aggregators', 3, 5450, NOW()),
    ('m2', 'Mustard', 'Alwar Procurement', 15, 5420, NOW()),
    ('m3', 'Mustard', 'Tonk Oil Mills', 22, 5400, NOW()),
    ('m4', 'Mustard', 'Jaipur Digital Hub', 50, 5380, NOW()),
    ('m5', 'Mustard', 'Farmer Connect Platform', 8, 5410, NOW());
```

---

## Database Relationships

```
farmers (1) ──── (many) sell_requests
                         │
                         │ (1) ──── (many) sell_photos
```

---

## Status Flow Diagram

```
┌─────────────┐
│   Pending   │  (Farmer created request, awaiting buyer review)
└──────┬──────┘
       │
       ├─→ [Farmer declines] → Declined ✗
       │
       └─→ [Buyer accepts] → Accepted ✓
              ↓
         ┌──────────────┐
         │   Accepted   │  (Buyer made offer, awaiting confirmation)
         └──────┬───────┘
                │
                └─→ [Farmer confirms] → Final Confirmed ✓✓
                                              ↓
                                    (Deal locked, ready to proceed)
```

---

## API Data Flow

### Creating a Sell Request

```
User Form Submit
    ↓
POST /market/sell/create
    ├─ FormData: crop, quantity, expected_price, harvest_date, photo1, photo2, photo3
    ↓
Backend (routes/marketplace.py)
    ├─ Validate farmer logged in
    ├─ Create SellRequest object
    ├─ Save photos to static/uploads/
    ├─ Create SellPhoto records
    ├─ Commit to database
    ↓
Response: JSON { success: true, request_id: "xxx" }
    ↓
JavaScript Redirect to /market/all-deals
    ↓
User sees deal in list
```

---

## Query Examples

### Get All Deals for a Farmer
```python
deals = SellRequest.query.filter_by(farmer_id='farmer-001').all()

# Returns:
# [
#   {id, crop_name, quantity, expected_price, status, ...},
#   {id, crop_name, quantity, expected_price, status, ...},
#   ...
# ]
```

### Get Deal with Photos
```python
deal = SellRequest.query.get('sell-001')
photos = SellPhoto.query.filter_by(request_id='sell-001').all()

# Result:
# deal.crop_name = 'Mustard'
# deal.quantity_quintal = 50
# deal.expected_price = 5450
# photos = [
#   {id, request_id, photo_url},
#   {id, request_id, photo_url},
#   {id, request_id, photo_url}
# ]
```

### Filter Deals by Status
```python
pending_deals = SellRequest.query.filter_by(
    farmer_id='farmer-001',
    status='pending'
).all()

# Same for: 'accepted', 'declined', 'final_confirmed'
```

### Update Deal Status
```python
deal = SellRequest.query.get('sell-001')
deal.status = 'accepted'
deal.buyer_price = 5420  # Set buyer's offer
db.session.commit()

# Can also:
# deal.status = 'declined'
# deal.status = 'final_confirmed'
# deal.final_price = 5420
```

---

## File Storage

Photos are saved to: `static/uploads/`

### Filename Format
```
{UUID}_{original_filename}

Example:
550e8400-e29b-41d4-a716-446655440000_crop.jpg
```

### Storage Path in Database
```
static/uploads/550e8400-e29b-41d4-a716-446655440000_crop.jpg
```

### Access URL
```
http://localhost:5000/static/uploads/550e8400-e29b-41d4-a716-446655440000_crop.jpg
```

---

## Database Setup

### Create Tables (Flask Migration)
```bash
# Generate migration
flask db migrate -m "Add sell requests and photos"

# Apply migration
flask db upgrade
```

### Manual Table Creation (if needed)
```sql
-- Run if migrations don't work

CREATE TABLE sell_requests (
    id VARCHAR(36) PRIMARY KEY,
    farmer_id VARCHAR(36) NOT NULL,
    crop_name VARCHAR(100) NOT NULL,
    quantity_quintal FLOAT NOT NULL,
    expected_price FLOAT NOT NULL,
    harvest_date VARCHAR(20),
    location VARCHAR(255),
    farmer_name VARCHAR(200),
    farmer_phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    buyer_price FLOAT,
    final_price FLOAT,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (farmer_id) REFERENCES farmers(id)
);

CREATE TABLE sell_photos (
    id VARCHAR(36) PRIMARY KEY,
    request_id VARCHAR(36) NOT NULL,
    photo_url VARCHAR(255) NOT NULL,
    FOREIGN KEY (request_id) REFERENCES sell_requests(id)
);
```

---

## Data Validation Rules

### SellRequest Fields
- `crop_name`: Required, max 100 chars
- `quantity_quintal`: Required, must be > 0
- `expected_price`: Required, must be > 0
- `harvest_date`: Required, should be in future
- `farmer_id`: Required, must exist in farmers table
- `status`: Default 'pending', must be valid status
- `location`: Optional, max 255 chars
- `farmer_name`: Optional, max 200 chars
- `farmer_phone`: Optional, max 20 chars

### SellPhoto Fields
- `request_id`: Required, must exist in sell_requests
- `photo_url`: Required, max 255 chars
- `id`: Auto-generated UUID

---

## Index Optimization

Recommended indexes for performance:
```sql
-- For fast farmer lookups
CREATE INDEX idx_sell_requests_farmer_id ON sell_requests(farmer_id);

-- For status filtering
CREATE INDEX idx_sell_requests_status ON sell_requests(status);

-- For date-based queries
CREATE INDEX idx_sell_requests_created_at ON sell_requests(created_at);

-- For photo lookups
CREATE INDEX idx_sell_photos_request_id ON sell_photos(request_id);

-- Composite index for common queries
CREATE INDEX idx_sell_requests_farmer_status ON sell_requests(farmer_id, status);
```

---

## Backup and Recovery

### Export Data
```bash
# Export sell_requests table
sqlite3 telhan_sathi.db "SELECT * FROM sell_requests;" > sell_requests_backup.csv

# Export sell_photos table
sqlite3 telhan_sathi.db "SELECT * FROM sell_photos;" > sell_photos_backup.csv
```

### Restore Data
```bash
# Restore from backup
sqlite3 telhan_sathi.db ".mode csv"
sqlite3 telhan_sathi.db ".import sell_requests_backup.csv sell_requests"
```

---

## Migration History

```
Revision: Initial schema
Date: 2025-12-03
Changes:
  - Created sell_requests table
  - Created sell_photos table
  - Added foreign keys to farmers table

Status: Active
```

---

## Common Issues & Solutions

### Issue: Photos not loading
- **Check**: Photo path in database
- **Check**: File exists in static/uploads/
- **Check**: File permissions (644 or 755)
- **Solution**: Verify photo_url path and ensure files are readable

### Issue: Duplicate photos
- **Cause**: Multiple uploads of same file
- **Solution**: Use UUID to generate unique filenames (already implemented)

### Issue: Status not updating
- **Check**: Session validation (farmer must be logged in)
- **Check**: Deal belongs to farmer
- **Solution**: Ensure farmer_id_verified is in session

### Issue: Photos disappear after reboot
- **Check**: Upload directory not persisted
- **Solution**: Use absolute path or configure upload directory properly
