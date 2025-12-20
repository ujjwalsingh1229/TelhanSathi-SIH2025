# Real-Time Bidding System - Quick Reference Guide

## 🎯 Quick Start

### Start the Server
```bash
cd backend
python app.py
```
Server runs on `http://localhost:5000` with WebSocket support

---

## 🗺️ Route Map

### Buyer Routes
| Route | Purpose |
|-------|---------|
| `/bidding/auction-browse` | Browse and filter auctions |
| `/bidding/auction-detail/<id>` | View auction and place bids |
| `/bidding/my-bids` | View bid history and status |

### Farmer Routes
| Route | Purpose |
|-------|---------|
| `/bidding/create-auction` | Create new auction listing |
| `/bidding/my-auctions` | Manage auctions and view earnings |

---

## 📡 API Endpoints Quick Reference

### Auctions (Buyer)
```
GET  /bidding/buyer/auctions              List live auctions (with filters)
GET  /bidding/buyer/auction/<id>          Get auction details
GET  /bidding/buyer/my-bids               Get buyer's bids
GET  /bidding/buyer/won-auctions          Get won transactions
```

### Auctions (Farmer)
```
POST /bidding/farmer/create-auction       Create new auction
GET  /bidding/farmer/my-auctions          Get farmer's auctions
GET  /bidding/farmer/auction/<id>         Get auction details with bids
POST /bidding/farmer/auction/<id>/end     End auction manually
```

### Prices
```
GET  /bidding/get-base-price/<crop>       Get base price for crop
GET  /bidding/crop-prices                 Get all crop prices
```

### Live Updates
```
GET  /bidding/auction/<id>/live-updates   Polling fallback for auction updates
GET  /bidding/stats                       Get system statistics
```

### Transactions
```
GET  /bidding/transaction/<id>            Get transaction details
POST /bidding/transaction/<id>/update-status  Update transaction status
```

### Notifications
```
GET  /bidding/notifications               Get user notifications
POST /bidding/notification/<id>/mark-read Mark notification as read
```

---

## 🔗 WebSocket Events

### Client → Server
```javascript
// Join auction room
socket.emit('join_auction', { auction_id: 'abc-123' });

// Place manual bid
socket.emit('place_bid', { 
    auction_id: 'abc-123', 
    bid_amount: 5650 
});

// Setup auto-bidding
socket.emit('auto_bid', {
    auction_id: 'abc-123',
    max_bid_amount: 6000,
    auto_increment: 250
});

// End auction (farmer only)
socket.emit('end_auction', { auction_id: 'abc-123' });

// Leave auction room
socket.emit('leave_auction', { auction_id: 'abc-123' });

// Get auction update (polling fallback)
socket.emit('get_auction_update', { auction_id: 'abc-123' });
```

### Server → Client
```javascript
// Bid placed
socket.on('bid_placed', (data) => {
    console.log(data.auction.current_bid);
});

// You were outbid
socket.on('you_were_outbid', (data) => {
    console.log(`Outbid! New bid: ₹${data.amount}`);
});

// Auction ended
socket.on('auction_ended', (data) => {
    console.log(`Winner: ${data.winning_buyer_id}`);
});

// Watcher count update
socket.on('watcher_update', (data) => {
    console.log(`${data.watcher_count} people watching`);
});
```

---

## 📊 Database Tables

### Auction Table
```python
id              String (PK)
seller_id       String (FK → Farmer.farmer_id)
crop_name       String (Soybean, Sunflower, etc.)
quantity        Float (Quintals)
base_price      Float (From Mandi API)
min_bid_price   Float
current_highest_bid Float
start_time      DateTime
end_time        DateTime
status          Enum (live, ended, sold, cancelled)
winning_buyer_id String
final_price     Float
photo1_path     String
photo2_path     String
photo3_path     String
description     Text
location        String
```

### Bid Table
```python
id              String (PK)
auction_id      String (FK → Auction.id)
buyer_id        String (FK → Buyer.buyer_id)
bid_amount      Float
bid_type        Enum (manual, auto)
max_bid_amount  Float (for auto-bidding)
auto_increment  Float (default 100)
is_winning      Boolean
is_outbid       Boolean
timestamp       DateTime
```

### Transaction Table
```python
id              String (PK)
auction_id      String (FK → Auction.id)
seller_id       String (FK → Farmer.farmer_id)
buyer_id        String (FK → Buyer.buyer_id)
crop_name       String
quantity        Float
final_price     Float
total_amount    Float
status          Enum (pending, confirmed, paid, delivered, completed)
payment_method  String
payment_date    DateTime
delivery_date   DateTime
```

---

## 🎨 Key CSS Classes

### Auction Card
```html
<div class="auction-card">
    <div class="auction-image"></div>
    <div class="auction-content"></div>
</div>
```

### Bid Card
```html
<div class="bid-card">
    <div class="bid-card-header"></div>
    <div class="bid-card-body"></div>
    <div class="bid-card-footer"></div>
</div>
```

### Status Badges
```html
<span class="status-badge status-live">LIVE</span>
<span class="status-badge status-sold">SOLD</span>
<span class="status-badge status-ended">ENDED</span>
```

### Buttons
```html
<button class="btn-primary">Primary Button</button>
<button class="btn-secondary">Secondary Button</button>
<button class="btn-icon">Icon Button</button>
```

---

## 🛠️ JavaScript Utilities

### WebSocket
```javascript
// Initialize WebSocket
initializeBiddingSocket();

// Join auction
joinAuctionRoom(auctionId);

// Place bid
placeBidSocket(auctionId, bidAmount);

// Setup auto-bid
setupAutoBidSocket(auctionId, maxBid, increment);
```

### Data Formatting
```javascript
formatCurrency(5500)      // "₹5,500"
formatNumber(5500)        // "5,500"
formatDate(dateString)    // "Dec 9, 10:30 AM"
getTimeRemaining(endTime) // "24h 30m"
```

### Notifications
```javascript
showNotification('Bid placed!', 'success');
showNotification('Failed to bid', 'error');
showNotification('You were outbid', 'warning');
```

### Validation
```javascript
validateBid(5650, 5500, 5500);      // { isValid: true, message: '✅' }
validateQuantity(50);               // { isValid: true, message: '✅' }
```

---

## 🔐 Authentication

### Farmer Login
```python
session['farmer_id_verified'] = farmer_id
session['farmer_name'] = farmer_name
```

### Buyer Login
```python
session['buyer_id_verified'] = buyer_id
session['buyer_name'] = buyer_name
```

### Decorator
```python
@farmer_login_required
def create_auction():
    return ...

@buyer_login_required
def place_bid():
    return ...
```

---

## 📋 Crop Types Supported

```
1. Soybean
2. Sunflower
3. Safflower
4. Groundnut
5. Castor
6. Mustard
7. Coconut
```

---

## ⏱️ Auction Durations

```
6 hours
12 hours
24 hours (1 day)
48 hours (2 days)
72 hours (3 days)
```

---

## 💰 Bidding Rules

1. **Minimum Bid:** ≥ Base Price (from Mandi API)
2. **Minimum Increment:** ₹100
3. **Auto-Bid Increment:** User can choose (₹100, 250, 500, 1000)
4. **All Bids:** Binding and non-refundable
5. **Winner:** Must complete transaction within 24 hours

---

## 🔍 Filter Options

### Auctions Filtering
```javascript
crop      // Soybean, Sunflower, etc.
max_price // Max base price (₹)
sort      // newest, ending_soon, price_low, price_high
location  // City/District
```

### My Bids Tabs
```
All Bids
Winning Bids
Outbid Bids
Ended Auctions
```

### My Auctions Tabs
```
All Auctions
Live Auctions
Ended Auctions
Sold Auctions
Cancelled Auctions
```

---

## 📊 Status Lifecycle

### Auction Status
```
created → live → ended → sold (if bids placed)
              → cancelled (if no bids)
```

### Bid Status
```
placed → winning (highest bid)
      → outbid (someone bid higher)
      → completed (auction ended, buyer won)
```

### Transaction Status
```
pending → confirmed → paid → delivered → completed
```

---

## 🚨 Error Messages

| Error | Solution |
|-------|----------|
| "Auction not found" | Check auction ID in URL |
| "You must log in" | Redirect to login page |
| "Bid too low" | Bid must exceed current highest |
| "Farm not found" | User not authenticated as farmer |
| "WebSocket disconnected" | Refresh page or check internet |

---

## ⚡ Performance Tips

1. **Real-Time:** Use WebSocket (avoid polling)
2. **Images:** Use WebP format when possible
3. **Caching:** Cache crop prices for 1 hour
4. **Validation:** Validate on client AND server
5. **Database:** Add indexes on seller_id, buyer_id
6. **Lazy Load:** Load bid history on-demand

---

## 🧪 Test Scenarios

### Scenario 1: Complete Auction
1. Farmer creates auction
2. Buyer 1 places bid (₹5,500)
3. Buyer 2 places bid (₹5,600)
4. Buyer 1 places higher bid (₹5,700)
5. Buyer 2 gets outbid notification
6. Auction ends
7. Buyer 1 is winner
8. Transaction created

### Scenario 2: Auto-Bidding
1. Buyer 1 enables auto-bid (max: ₹6,000, increment: ₹250)
2. Buyer 2 places bid (₹5,500)
3. Auto-bid increases to ₹5,750
4. Buyer 2 places bid (₹5,750)
5. Auto-bid increases to ₹6,000
6. Buyer 2 cannot outbid further
7. Buyer 1 wins

### Scenario 3: Manual End
1. Farmer creates auction
2. Auction runs for 1 hour
3. Farmer decides to end early
4. Clicks "End Auction"
5. Auction closes immediately
6. Highest bidder wins
7. Transaction created

---

## 📱 Mobile Support

**Responsive Breakpoints:**
- **Mobile:** < 480px (1 column)
- **Tablet:** 480-768px (2 columns)
- **Desktop:** > 768px (3+ columns)

**Touch Optimization:**
- Buttons minimum 48px × 48px
- Tap targets spaced 8px apart
- Full-width forms on mobile
- Large, readable text

---

## 🔄 Real-Time Flow Diagram

```
User 1 (Buyer)                    WebSocket Server           User 2 (Buyer)
     │                                  │                          │
     ├─ emit('join_auction')─────────→ │                          │
     │                                  ├─ create room            │
     │                          ┌────────┤ store connection        │
     │                          │        │                          │
     ├──────────────────────────┤        ├─ emit('join_auction')─→ │
     │                          │        │                          │
     ├─ emit('place_bid')────────────→ │                          │
     │   (₹5,500)                      ├─ validate bid            │
     │                          ┌──────→├─ update database         │
     │                          │        ├─ broadcast('bid_placed')│
     │                     ┌────┴───────→├──────────────────────→ │
     │                     │             │ (New highest: ₹5,500)   │
     │                     │             │                          │
     │                     │             │ ← emit('you_were_outbid')│
     │ ← ('you_were_outbid')            │ (Amount: ₹5,600)        │
     │   (notify user)                   │                          │
     │                                   │ ← broadcast('bid_placed')
     │                                   │ (Update UI)              │
     │                                   │                          │
     └───────────────────────────────────┴──────────────────────────┘
```

---

## 📚 Documentation Files

1. **BIDDING_SYSTEM_IMPLEMENTATION.md** - Complete backend guide
2. **FRONTEND_IMPLEMENTATION.md** - Frontend details
3. **SYSTEM_COMPLETE_SUMMARY.md** - Overall summary
4. **QUICK_REFERENCE.md** - This file

---

## 🆘 Troubleshooting

### WebSocket Not Connecting
```python
# Check if socketio is initialized in app.py
from ml.websocket_server import socketio as ws_socketio
ws_socketio.init_app(app)
```

### Bids Not Updating in Real-Time
```javascript
// Ensure Socket.IO client is loaded
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
```

### Database Errors
```bash
# Check migrations
flask db current
flask db upgrade

# Verify tables
python -c "from models_marketplace import *; from app import db; db.create_all()"
```

### Images Not Loading
```
Check /static/auction_photos/ directory exists
Verify file permissions (644 for files, 755 for directories)
```

---

## 📞 Support

**For Bugs:**
1. Check browser console (F12)
2. Check server logs
3. Verify database connection
4. Check file permissions

**For Features:**
Add request in Phase 5 planning document

**For Performance:**
Monitor server CPU/memory
Check database query times
Optimize with indexes

---

**Last Updated:** December 9, 2025  
**Version:** 1.0 (Production Ready)  
**Status:** ✅ Complete & Tested
