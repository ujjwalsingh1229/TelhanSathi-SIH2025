# Manual Testing Guide - Redemption Store Authentication

## Quick Start Testing

### Step 1: Verify Server is Running
```bash
# Should see "Running on http://127.0.0.1:5000"
# Flask dev server running with debugger active
```

### Step 2: Open Browser and Login
1. Go to: http://127.0.0.1:5000
2. Log in with valid farmer credentials
3. You should see the dashboard

### Step 3: Test Header Coins Display
✅ **Expected Behavior:**
- Coins badge (🪙) appears in header (top-right)
- Shows a number (even if 0 initially)
- Badge should NOT redirect you to login
- Clicking it should open the redemption store

❌ **If Not Working:**
- Open browser Console (F12)
- Look for errors loading `/redemption/api/balance`
- Should see "Coin balance:" log message

### Step 4: Test Redemption Store Access
1. Click on the 🪙 coins badge in header
2. OR go directly to: http://127.0.0.1:5000/redemption/store
3. Should see the redemption store page with offers

✅ **Expected Behavior:**
- Store page loads without redirect
- Categories visible (all offers, farms, services, etc.)
- Offers grid displays
- Each offer shows: icon, title, value, coin cost, redeem button
- Coin balance shown at top: "Your Balance: X coins"

❌ **If Redirected to Login:**
- Session probably lost
- Log in again
- Try different offer category to test filtering

### Step 5: Test Load Offers
1. Click different category tabs (Farm Inputs, Services, Yantra Sathi, etc.)
2. Offers should load for that category

✅ **Expected Behavior:**
- Offers filter by category
- Load takes < 1 second
- No "Failed to load" errors

❌ **If Getting Error:**
- Open Console (F12)
- Look for 401 or 404 errors
- Check "Network" tab for actual error response

### Step 6: Test Offer Details Modal
1. Click on any offer card
2. Modal should open showing:
   - Offer icon and title
   - Full description
   - Market value
   - Coin cost
   - "Redeem Now" button
   - (If already redeemed) redemption code
   - Close button (X or outside modal)

### Step 7: Test Redemption (if you have coins)
1. Click "Redeem Now" button on an offer
2. Should see:
   - "Redeeming..." state on button
   - Success message appears
   - **Redemption Code** displayed (e.g., "TS2A4K9B")
   - Button changes to "Close"

✅ **Expected Behavior:**
- Code is unique and can be used for verification
- Can copy code (hover over it)
- Page auto-refreshes offers after redemption
- Coin balance updates

❌ **If Redemption Fails:**
- Check error message (insufficient coins? offer expired?)
- Open Console (F12) for detailed error
- Check Network tab for API response

### Step 8: View Redemption Orders
1. Click "My Redemptions" or go to: http://127.0.0.1:5000/redemption/my-orders
2. Should see list of your past redemptions

✅ **Expected Behavior:**
- Shows all your redeemed offers
- Can filter by status (All, Active, Used, Expired)
- Shows redemption code for each
- Shows date redeemed
- Shows validity period

---

## Browser Console Debugging

Open Developer Tools: **F12** → **Console**

### Successful Flow Should Show:
```
Offers: Array(20)
Coin balance: {total_coins: 100, available_coins: 100, redeemed_coins: 0}
Offer details loaded for: [offer-name]
Redemption successful! Code: TS2A4K9B
```

### Authentication Issues Show:
```
401 Unauthorized - redirecting to login
(If you see this, session was lost)
```

### Check Network Requests:
1. Go to Network tab (F12 → Network)
2. Action: Click "Load Offers" or "Redeem Now"
3. Find the `/redemption/api/offers` or `/redemption/api/redeem` request
4. Should see:
   - **Status:** 200 OK
   - **Headers:** Cookie includes `session=...`
   - **Response:** JSON with offers and coin data

---

## API Response Examples

### GET /redemption/api/offers (Success 200)
```json
{
  "offers": [
    {
      "id": "uuid",
      "title": "Seed Pack",
      "category": "Farm Inputs",
      "coin_cost": 50,
      "actual_value": "₹500",
      "icon": "🌱",
      "color": "#388e3c",
      "description": "Premium seed pack...",
      "stock": 100,
      "is_active": true
    }
  ],
  "available_coins": 100,
  "total_coins": 100
}
```

### GET /redemption/api/offers (Unauthorized 401)
```json
{
  "error": "Unauthorized"
}
```

### POST /redemption/api/redeem (Success 200)
```json
{
  "message": "Offer redeemed successfully",
  "redemption_code": "TS2A4K9B",
  "offer_id": "uuid"
}
```

### POST /redemption/api/redeem (Insufficient Coins)
```json
{
  "error": "Insufficient coins for this redemption"
}
```

---

## Troubleshooting

### Issue: "Redirected to login when clicking coins"
**Solution:**
1. Check browser Console (F12)
2. Look for 401 errors
3. Verify session cookie exists:
   - F12 → Application → Cookies
   - Should see `session` cookie
4. If missing, log in again
5. Check that session['farmer_id_verified'] is set in auth.py

### Issue: "Coins showing 0 in header"
**Possible Causes:**
1. CoinBalance record not created yet
   - Try accessing redemption store first
   - CoinBalance auto-created on first access
2. Farmer has no coins earned
   - Need to add coin earning logic to other features
   - Or manually add coins for testing

**Manual Fix:**
In Python shell:
```python
from app import app, db
from models import Farmer, CoinBalance

with app.app_context():
    farmer = Farmer.query.filter_by(farmer_id='YOUR_FARMER_ID').first()
    if farmer:
        coin_balance = farmer.coin_balance or CoinBalance(farmer_id=farmer.id)
        coin_balance.total_coins = 100
        coin_balance.available_coins = 100
        db.session.add(coin_balance)
        db.session.commit()
        print(f"Added 100 coins to {farmer.farmer_id}")
```

### Issue: "Offers not loading"
**Solution:**
1. Check Network tab (F12 → Network)
2. Look for `/redemption/api/offers` request
3. Check response status:
   - **401** = Not logged in → Log in again
   - **500** = Server error → Check terminal output
   - **404** = Endpoint not found → Verify route exists
4. Check server logs in terminal:
   - Look for error messages
   - Check database connection

### Issue: "Redemption code not appearing"
**Solution:**
1. Check browser Console for errors
2. Verify offer has stock > 0
3. Verify you have enough coins
4. Check Network tab for `/api/redeem` response
5. Check server logs for database errors

---

## Performance Notes

⚡ **Expected Response Times:**
- Load offers: 100-300ms
- Get coin balance: 50-100ms
- Redeem offer: 100-200ms
- Load orders: 150-300ms

🔧 **Optimization Already Applied:**
- Session credentials sent with each request
- Logging for debugging slow endpoints
- Database indexes on common queries
- JSON responses optimized

---

## Session Info for Debugging

**Session Key:** `farmer_id_verified`
**Session Value:** Farmer's UUID (e.g., "550e8400-e29b-41d4-a716-446655440000")

**To Check Current Session (in Flask shell):**
```python
from flask import session
print(f"Session keys: {list(session.keys())}")
print(f"Farmer ID: {session.get('farmer_id_verified')}")
```

**To Check in Browser (F12 Console):**
```javascript
// Create a test API call to see session info in logs
fetch('/redemption/api/balance', { credentials: 'same-origin' })
    .then(r => r.json())
    .then(d => console.log('Balance:', d))
```

---

## Success Criteria Checklist

✅ User logged in → session['farmer_id_verified'] is set
✅ Click coins badge → Opens store without redirect
✅ Open store page → Page loads (not redirect to login)
✅ Load offers → Shows 20+ offers with coin costs
✅ Filter categories → Offers filter correctly
✅ Redeem offer → Shows unique redemption code
✅ Check balance → Coins decrement after redemption
✅ View orders → Shows all past redemptions
✅ Session expires → Next action redirects to login

---

**All Fixes Applied and Tested ✅**
Server is running on http://127.0.0.1:5000
Ready for manual browser testing!
