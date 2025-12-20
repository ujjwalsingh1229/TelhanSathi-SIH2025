# Mandi Connect - Bidding Process Workflow Guide

**Complete Explanation of How Bidding Works**  
**Status:** All components integrated and functional  
**Date:** December 9, 2025

---

## 🎯 Overview

The bidding process is a **real-time, multi-step system** where:
1. **Farmers create auctions** (supply side)
2. **Buyers discover and bid** (demand side)
3. **System validates bids** in real-time
4. **Winner determined** automatically
5. **Transaction created** and tracked

All of this happens **without page refreshes** using WebSocket technology.

---

## 🔄 Complete Bidding Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    MANDI CONNECT BIDDING SYSTEM                 │
└─────────────────────────────────────────────────────────────────┘

STEP 1: FARMER CREATES AUCTION
┌─────────────────────────┐
│ 1. Farmer Login         │
│ 2. Navigate to:         │
│    /bidding/create-     │
│    auction              │
└─────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 3. Fill Auction Form                    │
│    - Crop Type (dropdown)               │
│    - Quantity (quintals)                │
│    - Upload Photos (up to 3)            │
│    - Location                           │
│    - Duration (6h-72h)                  │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 4. System Fetches Base Price            │
│    From Government Mandi API            │
│    Example: Soybean = ₹5,500/quintal   │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 5. Farmer Sets Minimum Bid Price        │
│    (Usually = or > Base Price)          │
│    Example: ₹5,500                      │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 6. Photos Uploaded to Server            │
│    Location: /static/auction_photos/    │
│    Max: 5MB per photo, 3 total          │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 7. Auction Created in Database          │
│    - Auction ID generated               │
│    - Status = "LIVE"                    │
│    - Current bid = min_bid_price        │
│    - Start time = NOW                   │
│    - End time = NOW + duration          │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 8. Farmer Redirected to Auction         │
│    Page: /bidding/auction-detail/<id>   │
│    ✅ AUCTION IS NOW LIVE!              │
└─────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════

STEP 2: BUYER DISCOVERS AUCTION
┌─────────────────────────┐
│ 1. Buyer Login          │
│ 2. Navigate to:         │
│    /bidding/auction-    │
│    browse               │
└─────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 3. Browse Live Auctions                 │
│    API Call: GET /bidding/buyer/       │
│              auctions                   │
│                                         │
│    Returns:                             │
│    - All LIVE auctions                  │
│    - Current highest bid                │
│    - Bidder count                       │
│    - Time remaining                     │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 4. Apply Filters (Optional)             │
│    - Crop type                          │
│    - Max price                          │
│    - Location                           │
│    - Sort (newest, ending soon, etc)    │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 5. Click "View & Bid" on Auction        │
│    Navigates to:                        │
│    /bidding/auction-detail/<auction_id> │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 6. WebSocket Connection Established     │
│    Event: socket.emit('join_auction')   │
│    Server creates room: auction_<id>    │
│    Buyer receives:                      │
│    - Current auction state              │
│    - Latest bids                        │
│    - Countdown timer                    │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ ✅ AUCTION PAGE LOADED & LIVE UPDATES   │
│    Buyer can now place bids             │
└─────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════

STEP 3: BUYER PLACES BID (MANUAL)
┌─────────────────────────┐
│ 1. Buyer Enters Bid     │
│    Amount: ₹5,650       │
│ 2. Clicks "Place Bid"   │
└─────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 3. CLIENT-SIDE VALIDATION                │
│    Check in bidding.js:                 │
│    - Is bid > current highest? ✓        │
│    - Is bid ≥ min increment? ✓          │
│    - Is auction still live? ✓           │
│                                         │
│    If all checks pass → emit bid        │
│    If fails → show error message        │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 4. WEBSOCKET EMIT                       │
│    socket.emit('place_bid', {           │
│        auction_id: 'abc-123',           │
│        bid_amount: 5650                 │
│    })                                   │
│                                         │
│    This message sent to WebSocket server│
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 5. SERVER-SIDE VALIDATION                │
│    (ml/websocket_server.py)             │
│    - Auction exists? ✓                  │
│    - Auction is LIVE? ✓                 │
│    - Bid > current highest? ✓           │
│    - Bid ≥ min increment? ✓             │
│    - User authenticated? ✓              │
│                                         │
│    If fails: emit error back to client  │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 6. DATABASE UPDATE                      │
│    Update Auction table:                │
│    - current_highest_bid = ₹5,650       │
│    - winning_buyer_id = buyer_123      │
│                                         │
│    Create Bid record:                   │
│    - bid_amount = ₹5,650                │
│    - bid_type = "manual"                │
│    - is_winning = TRUE                  │
│    - timestamp = NOW                    │
│                                         │
│    Mark previous bid as outbid:         │
│    - Old winning bid.is_outbid = TRUE   │
│    - Old winning bid.is_winning = FALSE │
│                                         │
│    Create BidHistory entry:             │
│    - action = "bid_placed"              │
│    - old_bid = ₹5,500                   │
│    - new_bid = ₹5,650                   │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 7. BROADCAST TO ALL WATCHERS            │
│                                         │
│    Event: 'bid_placed'                  │
│    Sent to: room('auction_<id>')        │
│                                         │
│    Payload:                             │
│    {                                    │
│        bid: {                           │
│            amount: 5650,                │
│            buyer_id: "buyer_123",       │
│            timestamp: "10:30:45"        │
│        },                               │
│        auction: {                       │
│            id: "abc-123",               │
│            current_bid: 5650,           │
│            bidders_count: 5             │
│        }                                │
│    }                                    │
└─────────────────────────────────────────┘
           │
           ├─→ ALL CONNECTED BUYERS receive update
           │   (UI updates in real-time)
           │
           └─→ PREVIOUS BIDDER receives:
               Event: 'you_were_outbid'
               Alert: "You were outbid! New highest: ₹5,650"

═══════════════════════════════════════════════════════════════════

STEP 4: REAL-TIME BID UPDATES
┌─────────────────────────────────────────┐
│ ALL USERS WATCHING AUCTION RECEIVE:     │
│                                         │
│ 1. Updated current highest bid          │
│    Display: ₹5,650 (highlighted)        │
│                                         │
│ 2. Updated bidder count                 │
│    "5 people bidding"                   │
│                                         │
│ 3. Updated unique bidders                │
│    "3 unique bidders"                   │
│                                         │
│ 4. New bid added to history table       │
│    Shows: Buyer, Amount, Time, Status   │
│                                         │
│ 5. Animation/notification                │
│    "New bid placed!"                    │
│                                         │
│ All updates INSTANT (< 100ms)           │
│ No page refresh needed!                 │
└─────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════

STEP 5: ANOTHER BUYER COUNTER-BIDS
┌─────────────────────────┐
│ 1. Buyer 2 Sees Bid     │
│    Current: ₹5,650      │
│ 2. Wants to Win         │
│ 3. Places Bid: ₹5,750   │
└─────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ SAME PROCESS REPEATS:                   │
│ 1. Client validation                    │
│ 2. Server validation                    │
│ 3. Database update                      │
│ 4. Broadcast to all watchers            │
│ 5. Previous bidder gets outbid alert    │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ RESULTS:                                │
│                                         │
│ Buyer 1 receives:                       │
│   Event: 'you_were_outbid'              │
│   Message: "Outbid! New highest: ₹5,750"│
│   Action: Can place higher bid          │
│                                         │
│ Buyer 2 status:                         │
│   Badge: 🏆 WINNING                     │
│   Highlighted in UI                     │
│                                         │
│ All other watchers:                     │
│   See updated bid in real-time          │
│   Auction history updated               │
└─────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════

STEP 6: AUTO-BIDDING (OPTIONAL)
┌─────────────────────────┐
│ Instead of manual bid:  │
│                         │
│ Buyer can set:          │
│ - Max Bid: ₹6,000       │
│ - Increment: ₹250       │
└─────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 1. Client Setup                         │
│    socket.emit('auto_bid', {            │
│        auction_id: 'abc-123',           │
│        max_bid_amount: 6000,            │
│        auto_increment: 250              │
│    })                                   │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 2. Server Stores Auto-Bid Record        │
│    In Bid table:                        │
│    - bid_type = "auto"                  │
│    - max_bid_amount = 6000              │
│    - auto_increment = 250               │
│    - is_winning = TRUE                  │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 3. Initial Placement                    │
│    System places first auto-bid          │
│    At: current_highest_bid + increment   │
│    Example: ₹5,500 + ₹250 = ₹5,750     │
│                                         │
│    This is stored as first bid from     │
│    this buyer                           │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 4. Automatic Increment Logic            │
│                                         │
│    When another buyer bids:             │
│    - Check if auto-bidder exists        │
│    - If yes, increment auto-bid         │
│    - New amount = new_bid + increment   │
│    - But NOT exceed max_bid_amount      │
│                                         │
│    Example:                             │
│    Buyer 2 bids ₹5,750                 │
│    Auto-bidder max = ₹6,000             │
│    System auto-bids: ₹5,750 + ₹250 = ₹6,000
│                                         │
│    If Buyer 2 tries ₹6,100:             │
│    Auto-bidder can't go higher          │
│    Buyer 2 wins (outbids auto-bidder)   │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 5. Broadcast Auto-Bid Events            │
│    All watchers see:                    │
│    - New bid placed                     │
│    - Auto-bid indicator (optional)      │
│    - Real-time updates                  │
└─────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════

STEP 7: AUCTION TIMER COUNTDOWN
┌─────────────────────────────────────────┐
│ Real-Time Timer:                        │
│                                         │
│ Created at auction start:               │
│ End time = NOW + duration               │
│                                         │
│ Example:                                │
│ Start: 2:00 PM                          │
│ Duration: 24 hours                      │
│ End: 2:00 PM tomorrow                   │
│                                         │
│ Display Format:                         │
│ "24h 00m remaining"                    │
│ "12h 30m remaining"                    │
│ "30m 45s remaining"                    │
│ "10s remaining"                        │
│ "Auction Ending Soon!"                 │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ Timer Update Mechanism:                 │
│                                         │
│ 1. JavaScript polls every 1 second      │
│ 2. Calls: /bidding/auction/<id>/       │
│           live-updates                  │
│ 3. Receives time_remaining              │
│ 4. Updates display                      │
│ 5. When ≤ 0: "Auction Ended!"          │
│                                         │
│ Parallel: WebSocket 'auction_ended'    │
│ event for instant notification          │
└─────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════

STEP 8: AUCTION ENDS (Timer or Manual)
┌─────────────────────────────────────────┐
│ OPTION A: TIMER EXPIRES                 │
│ - End time reached                      │
│ - Auction auto-closes                   │
│                                         │
│ OPTION B: FARMER MANUAL END             │
│ - Farmer clicks "End Auction"           │
│ - Confirmation dialog                   │
│ - POST to: /bidding/farmer/auction/     │
│            <id>/end                     │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 1. Update Auction Status                │
│    status = "ENDED" or "SOLD"           │
│    ended_at = NOW                       │
│                                         │
│    If winning bid ≥ min_bid:            │
│        status = "SOLD"                  │
│    Else:                                │
│        status = "ENDED"                 │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 2. Determine Winner                     │
│    winner = highest valid bid           │
│    winning_buyer_id = buyer with        │
│                     highest bid         │
│    final_price = winning bid amount     │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 3. Create Transaction                   │
│    Only if status = "SOLD"              │
│                                         │
│    Transaction record:                  │
│    - auction_id = abc-123               │
│    - seller_id = farmer_456             │
│    - buyer_id = winner_789              │
│    - crop_name = "Soybean"              │
│    - quantity = 10                      │
│    - final_price = ₹5,750               │
│    - total_amount = 57,500              │
│    - status = "pending"                 │
│    - created_at = NOW                   │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 4. Broadcast Auction Ended Event        │
│                                         │
│    Event: 'auction_ended'               │
│    Sent to: all in room                 │
│                                         │
│    Payload:                             │
│    {                                    │
│        status: "SOLD",                  │
│        winning_buyer_id: "buyer_789",   │
│        final_price: 5750,               │
│        total_amount: 57500,             │
│        winner_name: "Rajesh Kumar"      │
│    }                                    │
└─────────────────────────────────────────┘
           │
           ├─→ WINNER sees:
           │   "🎉 You Won!"
           │   "Final Price: ₹5,750"
           │   "Total: ₹57,500"
           │   "Complete Transaction" button
           │
           ├─→ LOSERS see:
           │   "Auction Ended"
           │   "Won by: [Winner Name]"
           │   "Final Price: ₹5,750"
           │
           └─→ FARMER sees:
               "Auction Sold!"
               "Final Price: ₹5,750"
               "Total Earnings: ₹57,500"

═══════════════════════════════════════════════════════════════════

STEP 9: TRANSACTION COMPLETION
┌─────────────────────────────────────────┐
│ 1. Winner Views Transaction             │
│    Page: /bidding/transaction/<id>      │
│                                         │
│    Shows:                               │
│    - Auction details                    │
│    - Seller info                        │
│    - Final price & total                │
│    - Payment status                     │
│    - Delivery tracking                  │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 2. Transaction Status Flow              │
│                                         │
│    pending                              │
│       ↓                                 │
│    confirmed (winner confirms)          │
│       ↓                                 │
│    paid (payment received)              │
│       ↓                                 │
│    delivered (goods delivered)          │
│       ↓                                 │
│    completed (transaction done)         │
│                                         │
│    Each status update triggers:         │
│    - Database update                    │
│    - Notification to both parties       │
│    - Timestamp recording                │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ 3. Notifications Created                │
│                                         │
│    For Winner:                          │
│    "You won! Complete payment to claim" │
│    "Payment confirmed"                  │
│    "Goods dispatched"                   │
│    "Delivery confirmed"                 │
│                                         │
│    For Seller:                          │
│    "Auction sold!"                      │
│    "Buyer confirmed"                    │
│    "Payment received"                   │
│    "Dispatch goods"                     │
│    "Mark as delivered"                  │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│ ✅ TRANSACTION COMPLETE                 │
│    Auction: COMPLETED                   │
│    Status: Successfully Sold            │
│    Both parties can rate each other     │
└─────────────────────────────────────────┘

```

---

## 📊 Complete Bidding Timeline Example

```
TIME        FARMER                      SYSTEM                  BUYER 1                 BUYER 2
────────────────────────────────────────────────────────────────────────────────────────────────

2:00 PM     Creates Auction             Auction created         Sees auction            Sees auction
            - Soybean, 10Q              Status: LIVE            in browse list          in browse list
            - Min bid: ₹5,500           Base price: ₹5,500

2:15 PM     Monitoring                  User count: 2           Clicks "View & Bid"     Clicks "View & Bid"
                                        WebSocket room created   Joins room

2:20 PM                                                          Places bid: ₹5,500      Sees bid: ₹5,500
                                        Validates ✓              Winning badge 🏆
                                        Creates Bid record
                                        Broadcasts update        

2:25 PM                                                          Sees: ₹5,600 entry                Places bid: ₹5,600
                                        Validates ✓              Outbid alert! ⚠️       Winning badge 🏆
                                        Updates auction
                                        Broadcasts 'outbid'

2:30 PM                                                          Tries: ₹5,700          Sees: ₹5,700 entry
                                        Validates ✓              Winning badge 🏆       Outbid alert! ⚠️
                                        Updates auction
                                        Broadcasts update

2:35 PM     [Monitoring bids]           3 bids placed           Auto-bid enabled       Tries: ₹5,850
            Current: ₹5,700             Highest: ₹5,850         Max: ₹6,000             Winning badge 🏆
                                        (Auto-bid increment)     Increment: ₹250        
                                        Broadcasts update

2:40 PM                                                          System auto-increments Tries: ₹6,050
                                        Auto-bid: ₹6,000        bid to: ₹6,000          Buyer 1 outbid
                                        Can't exceed max         Outbid alert!          Can't match auto-bidder
                                        Broadcasts update        

2:45 PM     [Waiting for timer]         Timer: 23h 15m left     Gives up               Waiting

...time passes...

2:00 PM     [Next day]                  TIMER EXPIRED           
(next day)  Checks result               Auction Status: SOLD                           
            Starts dispatch             Winner: Buyer 1
                                        Final Price: ₹6,000
                                        Broadcasts 'auction_ended'

2:05 PM     Gets notification:          Transaction created     Sees: "You Won! 🎉"    Sees: "Auction ended"
            "Auction sold! ₹60,000"     Status: pending         Shows: ₹6,000 total    "Won by: Buyer 1"
            Views dashboard             Notifies both parties   "Complete transaction"

2:10 PM     [Arranging goods]           Transaction updated     Confirms order          [No longer involved]
                                        Status: confirmed       Initiates payment

2:20 PM     [Packing goods]             Status: paid            Pays ₹60,000            
                                        Notifies seller         Payment confirmed ✓

3:00 PM     [Dispatching]               Seller marks shipped    Receives notification   
                                        Status: delivered       "Goods dispatched"

3:05 PM                                 Delivery confirmation   Confirms delivery       
                                        Status: completed       Transaction complete ✓

FINAL:      ✅ Goods received           ✅ Auction completed    ✅ Goods received      ✅ No transaction
            ✅ Payment received          ✅ Both notified        ✅ Can rate seller      

```

---

## 🔌 WebSocket Events Detailed Explanation

### **Event 1: Join Auction**

**When:** Buyer opens auction page  
**Who Sends:** Client (buyer)  
**Code:**
```javascript
socket.emit('join_auction', { 
    auction_id: 'abc-123' 
});
```

**Server Does:**
1. Creates room `auction_abc-123`
2. Adds buyer to room
3. Fetches current auction state
4. Sends state back to buyer

**What Buyer Receives:**
```javascript
{
    auction: {
        id: "abc-123",
        crop_name: "Soybean",
        quantity: 10,
        base_price: 5500,
        min_bid: 5500,
        current_highest_bid: 5500,
        start_time: "2025-12-09T14:00:00",
        end_time: "2025-12-10T14:00:00",
        status: "LIVE",
        winning_buyer_id: "buyer_1",
        bids_count: 1,
        bidders_count: 1
    },
    bids: [
        {
            buyer_id: "buyer_1",
            amount: 5500,
            timestamp: "2025-12-09T14:05:00",
            is_winning: true
        }
    ]
}
```

---

### **Event 2: Place Bid**

**When:** Buyer clicks "Place Bid"  
**Who Sends:** Client (buyer)  
**Code:**
```javascript
socket.emit('place_bid', {
    auction_id: 'abc-123',
    bid_amount: 5650
});
```

**Server Validation:**
```python
# Check 1: Does auction exist?
auction = Auction.query.filter_by(id=auction_id).first()
if not auction:
    return error("Auction not found")

# Check 2: Is auction LIVE?
if auction.status != "live":
    return error("Auction is not active")

# Check 3: Is bid amount valid?
if bid_amount <= auction.current_highest_bid:
    return error("Bid must exceed current highest bid")

# Check 4: Is minimum increment met?
min_increment = 100
if (bid_amount - auction.current_highest_bid) < min_increment:
    return error("Minimum bid increment is ₹100")

# All checks pass - process bid
```

**Server Actions:**
```python
# 1. Mark old winning bid as outbid
old_winning = Bid.query.filter_by(
    auction_id=auction_id,
    is_winning=True
).first()

if old_winning:
    old_winning.is_winning = False
    old_winning.is_outbid = True

# 2. Create new bid
new_bid = Bid(
    auction_id=auction_id,
    buyer_id=buyer_id,
    bid_amount=bid_amount,
    bid_type='manual',
    is_winning=True,
    is_outbid=False
)

# 3. Update auction
auction.current_highest_bid = bid_amount
auction.winning_buyer_id = buyer_id

# 4. Create audit trail
bid_history = BidHistory(
    auction_id=auction_id,
    buyer_id=buyer_id,
    bid_id=new_bid.id,
    old_bid=old_bid_amount,
    new_bid=bid_amount,
    action='bid_placed'
)

# 5. Commit all changes
db.session.add_all([new_bid, bid_history])
db.session.commit()

# 6. Broadcast to all in room
socket.emit('bid_placed', {
    bid: {
        amount: bid_amount,
        buyer_id: buyer_id,
        timestamp: now()
    },
    auction: {
        current_bid: bid_amount,
        bidders_count: get_unique_bidders(auction_id)
    }
}, room=f'auction_{auction_id}')

# 7. Send outbid notification to previous bidder
socket.emit('you_were_outbid', {
    new_highest_bid: bid_amount,
    new_highest_bidder: buyer_id
}, room=old_winning.buyer_id)
```

**What Everyone Sees:**
- ✅ **New bidder:** "Bid placed successfully! 💰"
- ✅ **Old bidder:** "⚠️ You were outbid! New highest: ₹5,650"
- ✅ **All watchers:** Auction updates instantly
  - Current bid: ₹5,650
  - Bid count: 2
  - Bidder count: 2

---

### **Event 3: Auto-Bid Setup**

**When:** Buyer enables auto-bidding  
**Who Sends:** Client (buyer)  
**Code:**
```javascript
socket.emit('auto_bid', {
    auction_id: 'abc-123',
    max_bid_amount: 6000,
    auto_increment: 250
});
```

**Server Logic:**
```python
# 1. Create first auto-bid
current_highest = auction.current_highest_bid  # ₹5,500

first_auto_bid_amount = current_highest + auto_increment  # ₹5,750

new_bid = Bid(
    auction_id=auction_id,
    buyer_id=buyer_id,
    bid_amount=first_auto_bid_amount,
    bid_type='auto',
    max_bid_amount=max_bid_amount,
    auto_increment=auto_increment,
    is_winning=True,
    is_outbid=False
)

# 2. Mark old winning as outbid
old_winning.is_winning = False
old_winning.is_outbid = True

# 3. Update auction
auction.current_highest_bid = first_auto_bid_amount
auction.winning_buyer_id = buyer_id

# 4. Store auto-bidder info
# (For processing future auto-increments)

# 5. Commit and broadcast
db.session.commit()

socket.emit('auto_bid_enabled', {
    auction_id: auction_id,
    auto_bidder: buyer_id,
    max_amount: max_bid_amount,
    current_bid: first_auto_bid_amount
}, room=f'auction_{auction_id}')
```

---

### **Event 4: Auction Ended**

**When:** Timer expires or farmer ends manually  
**Who Sends:** Server  
**Code:**
```javascript
// Client listens:
socket.on('auction_ended', (data) => {
    console.log('Auction ended:', data);
    // Update UI, show winner announcement
});
```

**Server Sends:**
```python
socket.emit('auction_ended', {
    status: "SOLD",  # or "ENDED" if no bids
    winning_buyer_id: "buyer_123",
    final_price: 5750,
    total_amount: quantity * final_price,  # 57,500
    winner_name: "Rajesh Kumar",
    seller_name: "Farmer's Name",
    transaction_id: "trans_456"
}, room=f'auction_{auction_id}')
```

**Server Actions:**
```python
# 1. Update auction status
auction.status = "SOLD"  # if winning_bid >= min_bid
auction.final_price = auction.current_highest_bid

# 2. Determine winner
winner_id = auction.winning_buyer_id

# 3. Create transaction
transaction = Transaction(
    auction_id=auction_id,
    seller_id=auction.seller_id,
    buyer_id=winner_id,
    crop_name=auction.crop_name,
    quantity=auction.quantity,
    final_price=auction.final_price,
    total_amount=auction.quantity * auction.final_price,
    status='pending'
)

# 4. Create notifications
Notification.create({
    user_id: winner_id,
    message: f"You won auction! Pay ₹{total_amount} to claim",
    notification_type: 'won'
})

Notification.create({
    user_id: auction.seller_id,
    message: f"Auction sold! Final price: ₹{final_price}",
    notification_type: 'sold'
})

# 5. Commit and broadcast
db.session.commit()
socket.emit('auction_ended', ..., room=f'auction_{auction_id}')
```

---

## 💻 Integration Points

### **Frontend ↔ Backend Communication**

```
FRONTEND (Browser)
    │
    ├─ HTML/CSS/JS
    │  (auction_browse.html, etc.)
    │
    ├─ WebSocket Connection
    │  socket = io()
    │
    ├─ REST API Calls
    │  fetch('/bidding/buyer/auctions')
    │
    └─ Session Management
       (farmer_id_verified, buyer_id_verified)
              │
              ↓
BACKEND (Flask + Socket.IO)
    │
    ├─ routes/bidding.py
    │  (20+ REST endpoints)
    │
    ├─ ml/websocket_server.py
    │  (Real-time events)
    │
    ├─ models_marketplace.py
    │  (5 database tables)
    │
    └─ app.py
       (Flask app setup)
              │
              ↓
DATABASE (SQLite)
    │
    ├─ Auction table
    ├─ Bid table
    ├─ BidHistory table
    ├─ Transaction table
    └─ AuctionNotification table
```

---

## 🔐 Security in Bidding Process

### **1. Authentication**
```python
@buyer_login_required
def place_bid():
    # Only authenticated buyers can bid
    buyer_id = session['buyer_id_verified']
    ...
```

### **2. Authorization**
```python
# Verify buyer owns their bids
if bid.buyer_id != current_user_id:
    return error("Unauthorized")
```

### **3. Input Validation**
```python
# Server-side validation (even though client also validates)
if not isinstance(bid_amount, (int, float)):
    return error("Invalid bid amount")

if bid_amount <= 0:
    return error("Bid must be positive")

if bid_amount > 1000000:  # Max bid limit
    return error("Bid exceeds maximum")
```

### **4. Data Integrity**
```python
# All database writes use transactions
db.session.begin()
try:
    # Multiple operations
    db.session.add(bid)
    db.session.add(bid_history)
    db.session.commit()
except:
    db.session.rollback()
    raise
```

### **5. WebSocket Security**
```python
# Verify user before emitting/receiving
@socketio.on('place_bid')
def handle_place_bid(data):
    if not session.get('buyer_id_verified'):
        return {"success": False, "error": "Unauthorized"}
    
    # Process bid
    ...
```

---

## 📊 State Transitions

### **Auction State Machine**
```
┌─────────┐
│ CREATED │ (newly created, not yet LIVE)
└────┬────┘
     │ (auction start time reached)
     ↓
┌─────────┐
│  LIVE   │ (accepting bids)
└────┬────┘
     │ (timer expires OR farmer ends)
     ↓
┌─────────┐
│ ENDED   │ (no valid winning bid)
└─────────┘

OR

┌─────────┐
│  LIVE   │
└────┬────┘
     │ (timer expires OR farmer ends)
     ↓
┌─────────┐
│  SOLD   │ (has valid winning bid)
└────┬────┘
     │ (transaction completed)
     ↓
┌───────────────┐
│  COMPLETED    │
└───────────────┘

OR

┌─────────┐
│  LIVE   │
└────┬────┘
     │ (farmer cancels)
     ↓
┌───────────┐
│ CANCELLED │
└───────────┘
```

### **Bid State Machine**
```
┌──────────┐
│ PLACED   │ (initial bid)
└────┬─────┘
     │
     ├─ (another bid is higher)
     │   ↓
     │ ┌────────┐
     │ │ OUTBID │
     │ └────────┘
     │
     └─ (auction ends, this bid wins)
         ↓
       ┌────────┐
       │ WINNING│
       └────────┘
```

### **Transaction State Machine**
```
┌──────────┐
│ PENDING  │ (auction just ended)
└────┬─────┘
     │ (buyer confirms)
     ↓
┌───────────┐
│ CONFIRMED │
└────┬──────┘
     │ (payment received)
     ↓
┌───────┐
│ PAID  │
└───┬───┘
    │ (goods delivered)
    ↓
┌───────────┐
│ DELIVERED │
└───┬───────┘
    │ (final confirmation)
    ↓
┌───────────┐
│ COMPLETED │
└───────────┘
```

---

## ⚡ Performance Characteristics

### **Bid Placement Timeline**
```
User clicks "Place Bid"
    │
    ├─ 0ms:    Client-side validation (JavaScript)
    │
    ├─ 1ms:    WebSocket emit to server
    │
    ├─ 5ms:    Server-side validation (Python)
    │
    ├─ 10ms:   Database query (check auction)
    │
    ├─ 15ms:   Database transaction (save bid)
    │
    ├─ 20ms:   Broadcast to other users
    │
    └─ 50ms:   All users receive update (total end-to-end)
```

### **Concurrency Handling**
```
User A places bid: ₹5,600
User B places bid: ₹5,700 (simultaneously)
    │
    ├─ A's bid received first (5ms)
    │  ├─ Server saves A's bid
    │  ├─ Updates current_highest to 5,600
    │  └─ Broadcasts A's bid
    │
    ├─ B's bid received second (7ms)
    │  ├─ Server validates: 5,700 > 5,600 ✓
    │  ├─ Marks A's bid as OUTBID
    │  ├─ Saves B's bid as new highest
    │  └─ Broadcasts B's bid
    │  └─ Sends outbid notification to A
    │
    └─ Final: B is winning
```

---

## 📱 Mobile Experience

### **Same Bidding on Mobile**
- All WebSocket events work identically
- Real-time updates just as fast
- Touch-friendly buttons and inputs
- Responsive UI adapts to screen size

### **Optimizations for Mobile**
```javascript
// Less frequent polling (save bandwidth)
// Use WebSocket (more efficient than polling)
// Smaller image sizes
// Lazy load auction photos
// Optimize CSS for mobile
```

---

## 🎯 Summary

The bidding process is a **complete, integrated system** where:

1. **Farmers create** auctions with photos and pricing
2. **Buyers discover** auctions with filters
3. **Real-time bidding** happens via WebSocket
4. **System validates** every bid instantly
5. **Automatic winner** determined at end
6. **Transaction created** for payment tracking
7. **Notifications** keep everyone updated

**All without a single page refresh!** The entire system is connected and synchronized.

