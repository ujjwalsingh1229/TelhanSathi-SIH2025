# URL Reference & Navigation Map

## 🌐 All URLs in the Market Deal Flow

### Market Nearby Page
```
URL: http://localhost:5000/market/nearby/<crop>
Example: http://localhost:5000/market/nearby/Mustard

Returns: HTML page
Shows: Crop prices, average rate, nearby buyers
Actions: Click on price or average rate → navigate to deal review
```

### Deal Review Form Page
```
URL: http://localhost:5000/market/deal-review?crop=<crop>&price=<price>
Example: http://localhost:5000/market/deal-review?crop=Mustard&price=5450

Returns: HTML form
Shows: Crop info, price, photo upload, quantity, harvest date fields
Actions: Submit form → POST to /market/sell/create
```

### All Deals Page
```
URL: http://localhost:5000/market/all-deals

Returns: HTML page
Shows: List of all user's sell requests with status
Actions: 
  - Filter by status (All, Pending, Accepted, Declined, Confirmed)
  - Click on deal → navigate to deal details
```

### Deal Details Page
```
URL: http://localhost:5000/market/deal-details/<request_id>
Example: http://localhost:5000/market/deal-details/550e8400-e29b-41d4-a716-446655440000

Returns: HTML page
Shows: Full deal information, photos, status, actions
Actions: Accept/Decline/Negotiate based on status
```

---

## 📡 API Endpoints

### Get All Deals (JSON)
```
Method: GET
URL: http://localhost:5000/market/deals-list

Returns: JSON Array
Response Example:
[
  {
    "id": "sell-001",
    "crop_name": "Mustard",
    "quantity_quintal": 50,
    "expected_price": 5450,
    "buyer_price": null,
    "harvest_date": "2025-03-15",
    "status": "pending",
    "created_at": "2025-12-03T10:30:00"
  },
  ...
]
```

### Get Deal Data (JSON)
```
Method: GET
URL: http://localhost:5000/market/deal-data/<request_id>
Example: http://localhost:5000/market/deal-data/sell-001

Returns: JSON Object
Response Example:
{
  "id": "sell-001",
  "crop_name": "Mustard",
  "quantity_quintal": 50,
  "expected_price": 5450,
  "buyer_price": 5420,
  "final_price": null,
  "harvest_date": "2025-03-15",
  "location": "Village Khera, Bharatpur",
  "farmer_name": "Ramesh Kumar",
  "farmer_phone": "+91 9876543210",
  "status": "pending",
  "created_at": "2025-12-03T10:30:00",
  "photos": [
    { "id": "p1", "photo_url": "static/uploads/uuid1.jpg" },
    { "id": "p2", "photo_url": "static/uploads/uuid2.jpg" },
    { "id": "p3", "photo_url": "static/uploads/uuid3.jpg" }
  ]
}
```

### Create Sell Request
```
Method: POST
URL: http://localhost:5000/market/sell/create

Content-Type: multipart/form-data

Parameters:
  - crop: string (required)
  - quantity: float (required)
  - expected_price: float (required)
  - harvest_date: string (required, format: YYYY-MM-DD)
  - photo1: file (optional)
  - photo2: file (optional)
  - photo3: file (optional)

Example cURL:
curl -X POST http://localhost:5000/market/sell/create \
  -F "crop=Mustard" \
  -F "quantity=50" \
  -F "expected_price=5450" \
  -F "harvest_date=2025-03-15" \
  -F "photo1=@/path/to/photo1.jpg" \
  -F "photo2=@/path/to/photo2.jpg" \
  -F "photo3=@/path/to/photo3.jpg"

Returns: JSON
Response: { "success": true, "request_id": "sell-001" }
```

### Accept Deal
```
Method: POST
URL: http://localhost:5000/market/deal/<request_id>/accept
Example: http://localhost:5000/market/deal/sell-001/accept

Content-Type: application/json

Body:
{
  "final_price": 5420
}

Returns: JSON
Response: { "success": true, "final_price": 5420 }
```

### Decline Deal
```
Method: POST
URL: http://localhost:5000/market/deal/<request_id>/decline
Example: http://localhost:5000/market/deal/sell-001/decline

Returns: JSON
Response: { "success": true }
```

---

## 🗺️ User Navigation Map

### Scenario 1: Farmer Creates New Deal

```
Step 1: Go to market nearby page
        → http://localhost:5000/market/nearby/Mustard

Step 2: Click on average price card
        → JavaScript: goToDealReview('Mustard', 5432)
        → Navigate to: /market/deal-review?crop=Mustard&price=5432

Step 3: Fill form
        - Quantity: 50
        - Harvest Date: 2025-03-15
        - Upload 3 photos

Step 4: Click "Confirm & Accept" button
        → POST /market/sell/create (with form data)
        → Create SellRequest in database
        → Redirect to: /market/all-deals

Step 5: See new deal in list
        → New deal appears with "Pending" status
```

### Scenario 2: Farmer Views Existing Deal

```
Step 1: Go to all deals page
        → http://localhost:5000/market/all-deals

Step 2: Page loads via AJAX
        → GET /market/deals-list (JSON)
        → JavaScript renders deal cards

Step 3: Click on a deal
        → Navigate to: /market/deal-details/sell-001

Step 4: Deal details page loads
        → GET /market/deal-data/sell-001 (JSON)
        → JavaScript renders deal info and photos

Step 5: View deal information
        - Crop details
        - Photos in gallery
        - Current status
        - Action buttons (if pending)
```

### Scenario 3: Accept a Deal

```
Step 1: On deal details page
        → http://localhost:5000/market/deal-details/sell-001

Step 2: Enter final price
        - Input field shows: ₹5420 / Quintal

Step 3: Click "Confirm Price & Accept"
        → JavaScript: acceptDeal()
        → POST /market/deal/sell-001/accept
        → Send: { "final_price": 5420 }
        → Status changes to: "accepted"

Step 4: UI updates
        - Status badge becomes green
        - Buttons change to "Awaiting Confirmation"
```

---

## 📊 Status Codes

### Success Responses
```
200 OK - Request successful
201 Created - Resource created successfully
```

### Client Error Responses
```
400 Bad Request - Invalid data
401 Unauthorized - Not logged in
403 Forbidden - Don't have permission
404 Not Found - Resource doesn't exist
```

### Server Error Responses
```
500 Internal Server Error - Server error
```

---

## 🔐 Authentication

All endpoints except market/nearby require:
```
Session: farmer_id_verified
```

If not authenticated → redirect to login

---

## 📝 Sample Data Flow

### Creating a Deal - Request/Response

#### Request (HTML Form)
```
POST /market/sell/create
Content-Type: multipart/form-data

crop=Mustard
quantity=50
expected_price=5450
harvest_date=2025-03-15
photo1=[binary image data]
photo2=[binary image data]
photo3=[binary image data]
```

#### Backend Processing
```
1. Validate farmer is logged in
2. Check form data is valid
3. Create uploads directory (if needed)
4. Save photo1 → static/uploads/uuid1.jpg
5. Save photo2 → static/uploads/uuid2.jpg
6. Save photo3 → static/uploads/uuid3.jpg
7. Create SellRequest record
8. Create SellPhoto record 1
9. Create SellPhoto record 2
10. Create SellPhoto record 3
11. Commit to database
```

#### Response
```
{
  "success": true,
  "request_id": "sell-001"
}
```

#### Redirect
```
window.location.href = "/market/all-deals"
```

---

## 🎯 Quick Navigation Reference

| Action | From Page | To Page | URL |
|--------|-----------|---------|-----|
| View prices | Dashboard | Market Nearby | `/market/nearby/Mustard` |
| Create deal | Market Nearby | Deal Review | `/market/deal-review?crop=X&price=Y` |
| Submit deal | Deal Review | All Deals | `/market/all-deals` (via POST) |
| View deals | Dashboard | All Deals | `/market/all-deals` |
| View details | All Deals | Deal Details | `/market/deal-details/<id>` |
| Back | Deal Details | All Deals | Back button or `/market/all-deals` |
| Accept | Deal Details | Updated page | POST action |
| Decline | Deal Details | Updated page | POST action |

---

## 🌐 HTTP Methods Reference

| Method | Purpose | Example |
|--------|---------|---------|
| GET | Retrieve data/page | `/market/all-deals` |
| POST | Submit form/action | `/market/sell/create` |
| PUT | Update data | Not used yet |
| DELETE | Delete data | Not used yet |

---

## 📱 Mobile Navigation

All pages are mobile-responsive. Navigation works the same on:
- Desktop browsers
- Tablet browsers
- Mobile browsers

Frame size: 420px (mobile width) to 100% (responsive)

---

## 🔗 Deep Linking

Direct URL access:
```
Market Nearby: http://localhost:5000/market/nearby/Mustard
Deal Review: http://localhost:5000/market/deal-review?crop=Mustard&price=5450
All Deals: http://localhost:5000/market/all-deals
Deal Details: http://localhost:5000/market/deal-details/550e8400-e29b-41d4-a716-446655440000
```

All deep links work directly (after login).

---

## 🔙 Browser History

Back button behavior:
```
Market Nearby ← Deal Review ← All Deals ← Deal Details
  (back)         (back)        (back)

JavaScript history.back() implemented on:
- Deal Review page
- All Deals page  
- Deal Details page
```

---

## 💾 Session Management

Session key: `farmer_id_verified`

Check location: Session object (Flask)

Required for: All page routes

Optional for: Market nearby (shows all users but limited functionality)

---

## ⏱️ Timing

Expected response times:
```
Market Nearby: < 500ms
Deal Review: < 200ms
All Deals (JSON): < 300ms
Deal Details (JSON): < 300ms
Photo Upload: 1-5 seconds (depends on file size)
```

---

## 🔄 Redirect Chains

Deal creation flow:
```
Deal Review Form
    ↓ (submit)
POST /market/sell/create
    ↓ (success)
Redirect to /market/all-deals
    ↓ (browser loads)
All Deals page
```

Total: 1 redirect

---

## 📋 Form Submission Flow

```
User submits deal review form
    ↓
JavaScript validates form
    ↓
Show loading spinner
    ↓
POST to /market/sell/create
    ↓
Backend validates and saves
    ↓
Return success JSON
    ↓
JavaScript redirects
    ↓
User sees all deals page
```

---

## 🎓 Learning Path

New to the system? Follow this order:
1. Read QUICK_START.md - Understand the flow
2. Visit `/market/nearby/Mustard` - See market page
3. Click a price - Go to deal review
4. Read IMPLEMENTATION_SUMMARY.md - Understand architecture
5. Check CHANGES_DETAILED.md - See code changes
6. Review DATABASE_SCHEMA.md - Understand data structure
7. Read this file - Understand URLs and navigation

---

## 🚀 Deployment Checklist

Before going to production:
- [ ] Update all `localhost:5000` URLs to production domain
- [ ] Configure DATABASE_URL environment variable
- [ ] Set SECRET_KEY in environment
- [ ] Configure CORS with production domain
- [ ] Set up SSL/HTTPS
- [ ] Configure file upload directory (writable, backed up)
- [ ] Set up logging
- [ ] Test all endpoints
- [ ] Test photo uploads
- [ ] Test database operations
- [ ] Set up backups

---

## 📞 Troubleshooting URLs

If you can't access a page:

1. **Market Nearby 404**
   - Check crop name spelling
   - Should be: `/market/nearby/Mustard` (capital M)

2. **Deal Review 404**
   - Check URL has query parameters
   - Should be: `/market/deal-review?crop=Mustard&price=5450`
   - Missing `?crop=...` will fail

3. **All Deals 404**
   - Check you're logged in
   - Should redirect to login if not authenticated

4. **Deal Details 404**
   - Check deal ID is correct
   - Check you own the deal (not another farmer's deal)

5. **Photo not loading**
   - Check image path in database
   - Check file exists in static/uploads/
   - Check file permissions

---

Version: 1.0
Last Updated: December 3, 2025
