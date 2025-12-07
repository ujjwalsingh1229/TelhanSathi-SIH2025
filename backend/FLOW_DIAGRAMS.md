# Authentication Flow Diagram

## Session Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER LOGIN FLOW                              │
└─────────────────────────────────────────────────────────────────┘

1. UNAUTHENTICATED STATE
   ├─ session = {} (empty)
   ├─ Browser: No session cookie
   └─ All /redemption/* endpoints → 401 Unauthorized

2. USER VISITS /LOGIN PAGE
   ├─ GET /login → Shows login form
   └─ Page ready for credentials

3. USER SUBMITS LOGIN FORM
   ├─ POST /auth/login
   ├─ Validates farmer credentials ✓
   └─ Creates session record:
      └─ session['farmer_id_verified'] = farmer.id (UUID string)
         └─ Example: "550e8400-e29b-41d4-a716-446655440000"

4. SERVER SENDS SESSION COOKIE
   ├─ Response header: Set-Cookie: session=encrypted_cookie_value
   ├─ Browser stores cookie
   └─ Subsequent requests include cookie automatically

5. USER REDIRECTED TO DASHBOARD
   ├─ GET /dashboard
   ├─ Server checks session['farmer_id_verified'] ✓
   ├─ Page loads with authenticated content
   └─ Header shows coins badge with coin count

6. USER INTERACTION WITH REDEMPTION
   ├─ CLICK: Coins badge (🪙)
   │  └─ GET /redemption/api/balance
   │     ├─ Browser sends: Cookie: session=...
   │     ├─ Server extracts: farmer_id_verified from session
   │     ├─ Server queries: Farmer.query.get(farmer_id_verified)
   │     ├─ Server returns: { available_coins: 100, ... }
   │     └─ Header updates: Shows "100"
   │
   ├─ CLICK: "Redemption Store" link
   │  └─ GET /redemption/store
   │     ├─ Server checks: session['farmer_id_verified'] ✓
   │     ├─ Server renders: Store page template
   │     └─ Page loads with offers
   │
   ├─ FILTER: By category
   │  └─ GET /redemption/api/offers?category=farm_inputs
   │     ├─ Browser sends: Cookie: session=...
   │     ├─ Server checks: session['farmer_id_verified'] ✓
   │     ├─ Server returns: { offers: [...], available_coins: 100, ... }
   │     └─ Page displays: Offers with prices
   │
   └─ REDEEM: Click "Redeem Now"
      └─ POST /redemption/api/redeem
         ├─ Browser sends: Cookie: session=... + JSON body
         ├─ Server checks: session['farmer_id_verified'] ✓
         ├─ Server checks: Sufficient coins ✓
         ├─ Server deducts coins
         ├─ Server generates: Redemption code (TS2A4K9B)
         └─ Server returns: { redemption_code: "TS2A4K9B", ... }

7. SESSION EXPIRES (after inactivity or logout)
   ├─ session['farmer_id_verified'] removed
   ├─ Next API call:
   │  └─ GET /redemption/api/offers
   │     ├─ Server checks: session.get('farmer_id_verified') = None
   │     └─ Server returns: 401 Unauthorized { error: "Unauthorized" }
   │
   ├─ Frontend receives 401:
   │  └─ window.location.href = '/login'
   │
   └─ User redirected to login page
      └─ Back to state 1 (unauthenticated)
```

---

## Request/Response Cycle (Before vs After)

### BEFORE (Broken ❌)

```
User Logged In (session exists)
       │
       ├─ Click coins badge
       │  └─ GET /redemption/api/balance
       │     ├─ Check: session.get('farmer_id') ← WRONG KEY
       │     ├─ Result: None (key doesn't exist)
       │     └─ Returns: 401 Unauthorized
       │
       └─ Browser receives 401
          ├─ No handler for 401
          ├─ Throws error
          └─ Redirects to /login ← UNWANTED!

Result: Even though logged in, gets redirect to login!
```

### AFTER (Fixed ✅)

```
User Logged In (session exists)
       │
       ├─ Click coins badge
       │  └─ GET /redemption/api/balance
       │     │  (Browser includes: Cookie: session=...)
       │     ├─ Check: session.get('farmer_id_verified') ← CORRECT KEY
       │     ├─ Get farmer: Farmer.query.get(farmer_id_verified) ✓
       │     └─ Returns: 200 OK with coin data
       │
       └─ Browser receives 200
          ├─ Header updates with coin count
          ├─ No redirect needed
          └─ User stays on page ✓

Result: Works as expected! ✅
```

---

## Authentication Check Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              EVERY API REQUEST: Authentication Check            │
└─────────────────────────────────────────────────────────────────┘

API Endpoint receives request:
  │
  ├─ Call get_current_farmer()
  │  └─ Extract: farmer_id_verified = session.get('farmer_id_verified')
  │     │
  │     ├─ farmer_id_verified is None?
  │     │  └─ logger.warning("No farmer_id_verified in session")
  │     │  └─ return None
  │     │
  │     └─ farmer_id_verified exists?
  │        ├─ Query database: Farmer.query.get(farmer_id_verified)
  │        ├─ logger.debug(f"Farmer query result: {farmer}")
  │        └─ return farmer or None
  │
  ├─ Check result of get_current_farmer()
  │  │
  │  ├─ farmer is None?
  │  │  ├─ logger.warning("No farmer found in endpoint")
  │  │  ├─ return jsonify({'error': 'Unauthorized'}), 401
  │  │  └─ Browser receives 401
  │  │     └─ Frontend redirects to /login
  │  │
  │  └─ farmer exists?
  │     ├─ logger.debug(f"Found farmer: {farmer.farmer_id}")
  │     └─ Continue with business logic ✓
  │
  └─ Return response to browser

Success: 200 OK
Failure: 401 Unauthorized
```

---

## Data Flow Diagram

```
Browser                          Server                       Database
─────────────────────────────────────────────────────────────────────

User Login:
  ├─ POST /login ──────────────→ ├─ Validate credentials
  │                              │  └─ Query Farmer table
  │                              │     └─ Get farmer.id (UUID)
  │                              │
  │                              ├─ Set session:
  │                              │  └─ session['farmer_id_verified'] = UUID
  │                              │
  │ ←────────────────────── 302 + Set-Cookie: session=...
  │
  Store cookie

Access Redemption Store:
  ├─ GET /redemption/store ─────→ ├─ get_current_farmer()
  │  Cookie: session=...         │  └─ Extract UUID from session ✓
  │                              │  └─ Query: Farmer.get(UUID)
  │                              │     └─ Return farmer ✓
  │                              │
  │                              ├─ Check farmer exists ✓
  │                              │
  │                              ├─ ensure_coin_balance(farmer)
  │                              │  └─ Query: CoinBalance.get(farmer_id)
  │                              │     └─ Return or create
  │                              │
  │ ←────────────────────── 200 + HTML store page
  │
  Render page

Load Offers:
  ├─ GET /api/offers ───────────→ ├─ get_current_farmer() ✓
  │  Cookie: session=...         │
  │                              ├─ ensure_coin_balance(farmer)
  │                              │
  │                              ├─ Query: RedemptionOffer
  │                              │        .filter_by(is_active=True)
  │                              │  └─ Returns 20 offers
  │                              │
  │ ←────────────────────── 200 JSON
  │  {
  │    "offers": [...],
  │    "available_coins": 100,
  │    "total_coins": 100
  │  }
  │
  Display offers

Redeem Offer:
  ├─ POST /api/redeem ──────────→ ├─ get_current_farmer() ✓
  │  Cookie: session=...         │
  │  Body: {offer_id: "123"}     │  ├─ ensure_coin_balance(farmer)
  │                              │  ├─ Query: RedemptionOffer.get(123)
  │                              │  ├─ Check: coins sufficient ✓
  │                              │  ├─ Check: stock > 0 ✓
  │                              │  │
  │                              │  ├─ Create: FarmerRedemption record
  │                              │  │  └─ UPDATE: farmer_redemptions table
  │                              │  │
  │                              │  ├─ Update: CoinBalance
  │                              │  │  └─ available_coins -= cost
  │                              │  │  └─ UPDATE: coin_balances table
  │                              │  │
  │                              │  ├─ Create: CoinTransaction (audit log)
  │                              │  │  └─ INSERT: coin_transactions table
  │                              │  │
  │ ←────────────────────── 200 JSON
  │  {
  │    "redemption_code": "TS2A4K9B",
  │    "message": "Offer redeemed successfully"
  │  }
  │
  Display code
```

---

## Error Scenarios

### Scenario 1: Session Expired

```
Browser has stale session cookie
       │
       ├─ GET /redemption/api/offers
       │  Cookie: session=expired_cookie
       │
       └─→ Server
           ├─ Try to decrypt session cookie
           ├─ Cookie invalid/expired
           ├─ session.get('farmer_id_verified') → None
           ├─ get_current_farmer() → None
           │
           └─ return 401 Unauthorized
              ↓
           Frontend receives 401
           ├─ Detects: if (resp.status === 401)
           ├─ Redirects: window.location.href = '/login'
           └─ User sees login page
```

### Scenario 2: Insufficient Coins

```
User clicks "Redeem Now"
       │
       └─→ POST /redemption/api/redeem
           ├─ get_current_farmer() ✓ (logged in)
           ├─ ensure_coin_balance() ✓
           ├─ Get offer ✓
           ├─ Check: available_coins (50) < cost (100)?
           │  └─ YES → Insufficient
           │
           └─ return 400 Bad Request
              {
                "error": "Insufficient coins",
                "required": 100,
                "available": 50
              }
              ↓
           Frontend displays error message
```

### Scenario 3: Invalid Offer

```
User tries to redeem non-existent offer
       │
       └─→ POST /redemption/api/redeem
           ├─ get_current_farmer() ✓
           ├─ Query: RedemptionOffer.get("invalid_id")
           │  └─ Returns: None
           ├─ Check: if not offer?
           │  └─ YES → Not found
           │
           └─ return 404 Not Found
              { "error": "Offer not found" }
              ↓
           Frontend displays error message
```

---

## Session Security

```
┌─────────────────────────────────────────────────────────────────┐
│                    Session Configuration                        │
└─────────────────────────────────────────────────────────────────┘

SESSION_COOKIE_SECURE = False
  └─ For development (should be True in HTTPS production)

SESSION_COOKIE_HTTPONLY = True
  └─ ✓ Prevents JavaScript from accessing session cookie
  └─ Protects against XSS attacks

SESSION_COOKIE_SAMESITE = 'Lax'
  └─ ✓ Prevents sending cookie to cross-site requests
  └─ Protects against CSRF attacks

SECRET_KEY = 'dev-secret-key-...'
  └─ ✓ Encrypts session data
  └─ Should be changed in production

Session Storage:
  ├─ Encrypted in browser as cookie
  ├─ Decrypted server-side on each request
  ├─ Contains: { 'farmer_id_verified': 'uuid-string', ... }
  └─ Expires after configured timeout
```

---

## Complete User Journey

```
DAY 1 - First Time:
  1. Open browser → /login page
  2. Enter credentials → session created
  3. Redirected to /dashboard
  4. Click coins badge → Fails (0 coins to start)
  5. Explore redemption store
  6. No offers redeemable (no coins)
  7. Close browser → Session ends

DAY 2 - Earn Coins:
  1. Open browser → /login page
  2. Enter credentials → NEW session created
  3. Complete some activity → Earn 50 coins
     └─ API adds coins to coin_balance
  4. Refresh page → Coin count updates to 50
  5. Browse redemption offers
  6. Find offer for 50 coins → Now redeemable
  7. Click "Redeem Now"
  8. Get code → "TS2A4K9B"
  9. Go to service provider with code
  10. Use redemption code → Mark as used

DAY 3 - View History:
  1. Open browser → /login page
  2. Enter credentials → NEW session created
  3. Click coins badge → Shows 0 available (50 redeemed)
  4. Click "My Redemptions"
  5. See previous redemption
     └─ Status: "Used"
     └─ Code: "TS2A4K9B"
     └─ Date redeemed: Yesterday
     └─ Expires: 30 days from redemption

Session Management:
  • Each login creates NEW session
  • Session destroyed on logout
  • Session destroyed after 24-48 hours inactivity
  • Each session is independent
  • Multiple simultaneous sessions possible
```

---

**This diagram shows the complete authentication flow that is now working correctly! ✅**
