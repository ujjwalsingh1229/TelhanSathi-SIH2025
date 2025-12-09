# Live Oilseed Prices Module - Complete Documentation

## 📋 Overview

The Live Oilseed Prices module is a comprehensive system that fetches, displays, and analyzes real-time market prices for various oilseeds across India. It integrates with the Government of India's public API to provide farmers with up-to-date pricing information from multiple markets (mandis).

**Target Users:** Farmers and buyers interested in oilseed commodities  
**Supported Oilseeds:** Soybean, Mustard, Groundnut, Sunflower, Safflower, Sesame, Coconut

---

## 🏗️ Architecture

### System Flow

```
Government API (data.gov.in)
        ↓
Government API Data ✓ → Fallback to Database → Fallback to Mock Data
        ↓                        ↓                          ↓
    Parse Prices          Database Records          Demo Prices
        ↓                        ↓                          ↓
    ╔═══════════════════════════════════════════════════════════╗
    ║           Calculate Statistics (Avg, Min, Max)             ║
    ╚═══════════════════════════════════════════════════════════╝
        ↓
    ╔═══════════════════════════════════════════════════════════╗
    ║              Return JSON API Response                      ║
    ╚═══════════════════════════════════════════════════════════╝
        ↓
Frontend (HTML/JavaScript + Chart.js)
        ↓
Display Price Cards → User Clicks Crop → Show Price History Chart
```

---

## 🔧 Backend Implementation

### File: `routes/crop_economics.py`

#### 1. **Configuration**

```python
# Government API Details
GOVT_API_KEY = "579b464db66ec23bdd00000139dd36efa19740c954f95d9ca3b5abd0"
GOVT_API_BASE = "https://api.data.gov.in/resource/9ef84268-d588-465a-a5c3-375cda092f58"

# Supported Oilseeds
OILSEEDS = {
    'soybean': {'name': 'Soybean', 'unit': 'per quintal', 'icon': '🫘', 'api_name': 'Soyabean'},
    'mustard': {'name': 'Mustard', 'unit': 'per quintal', 'icon': '🌾', 'api_name': 'Mustard'},
    'groundnut': {'name': 'Groundnut', 'unit': 'per quintal', 'icon': '🫘', 'api_name': 'Groundnut'},
    'sunflower': {'name': 'Sunflower', 'unit': 'per quintal', 'icon': '🌻', 'api_name': 'Sunflower'},
    'safflower': {'name': 'Safflower', 'unit': 'per quintal', 'icon': '🌻', 'api_name': 'Safflower'},
    'sesame': {'name': 'Sesame', 'unit': 'per kg', 'icon': '🌾', 'api_name': 'Sesame'},
    'coconut': {'name': 'Coconut', 'unit': 'per piece', 'icon': '🥥', 'api_name': 'Coconut'},
}
```

#### 2. **Core Functions**

##### `fetch_live_prices_from_api(commodity_name)`

**Purpose:** Fetch live prices with 3-tier fallback system

**Process:**
1. **Try Government API First**
   - Sends request to `data.gov.in` API
   - Filters by commodity name
   - Parses response records
   - Handles multiple field name variations (modal_price, price, avg_price, close_price)

2. **Fallback to Database**
   - Queries `MarketPrice` table
   - Filters by commodity name (case-insensitive)
   - Orders by most recent first
   - Takes top 50 records

3. **Fallback to Mock Data**
   - Returns realistic demo prices
   - Used for demonstration when no real data available

**Returns:** List of price objects
```python
[
    {
        'price': 5500.50,
        'market': 'Mumbai Mandi',
        'state': 'Maharashtra',
        'date': '2024-12-09',
        'min_price': 5200.00,
        'max_price': 5800.00
    },
    ...
]
```

##### `get_mock_prices(commodity_name)`

**Purpose:** Generate realistic demo price data

**Features:**
- Base prices for each commodity
- Random variations (±₹500)
- Multiple markets simulated
- Current date timestamp

**Returns:** List of mock price objects

##### `get_mock_price_history(crop_key, days=180)`

**Purpose:** Generate 12 months of historical monthly price data

**Process:**
1. Gets current date
2. Loops back 12 months
3. For each month:
   - Calculates date
   - Applies trend (gradual price increase ₹30/month)
   - Adds random variation (±₹300)
   - Ensures positive minimum price (₹1500)

**Returns:** List of monthly history objects
```python
[
    {
        'date': '2024-12-01',
        'month': 'Dec 2024',
        'price': 5500.00,
        'count': 15
    },
    ...
]
```

---

## 🌐 API Endpoints

### 1. **GET `/crop-economics/dashboard`**

**Purpose:** Serve the crop economics dashboard page

**Authentication:** Required (login_required decorator)

**Response:** HTML page with embedded JavaScript

**Usage:**
```
GET http://localhost:5000/crop-economics/dashboard
```

---

### 2. **GET `/crop-economics/api/prices`**

**Purpose:** Fetch live prices for ALL oilseeds

**Authentication:** Required

**Response Format:**
```json
{
  "soybean": {
    "crop_name": "Soybean",
    "average": 5500.50,
    "max": 6000.00,
    "min": 5200.00,
    "count": 8,
    "unit": "per quintal",
    "icon": "🫘",
    "trend": "live",
    "source": "Government API",
    "markets": [
      {
        "price": 5500.50,
        "market": "Mumbai Mandi",
        "state": "Maharashtra",
        "date": "2024-12-09",
        "min_price": 5200.00,
        "max_price": 5800.00
      },
      ...
    ]
  },
  "mustard": { ... },
  ...
}
```

**Usage in Frontend:**
```javascript
fetch('/crop-economics/api/prices', { credentials: 'same-origin' })
  .then(r => r.json())
  .then(prices => {
    // Display price cards
  })
```

---

### 3. **GET `/crop-economics/api/price-history/<crop>`**

**Purpose:** Fetch 12-month historical price data for a specific crop

**Authentication:** Required

**Parameters:**
- `crop` (URL param): Crop key (e.g., 'soybean', 'mustard')

**Response Format:**
```json
{
  "crop": "Soybean",
  "history": [
    {
      "date": "2024-12-01",
      "month": "Dec 2024",
      "price": 5500.00,
      "count": 15
    },
    {
      "date": "2024-11-01",
      "month": "Nov 2024",
      "price": 5470.00,
      "count": 18
    },
    ...
  ],
  "source": "Mock Data (Demo)"
}
```

**Usage in Frontend:**
```javascript
fetch(`/crop-economics/api/price-history/${cropKey}`)
  .then(r => r.json())
  .then(data => {
    // Render chart
  })
```

---

### 4. **GET `/crop-economics/api/comparison`**

**Purpose:** Get live price comparison across all crops

**Authentication:** Required

**Response Format:**
```json
[
  {
    "crop": "Soybean",
    "price": 5500.50,
    "icon": "🫘",
    "count": 8
  },
  {
    "crop": "Mustard",
    "price": 6200.00,
    "icon": "🌾",
    "count": 10
  },
  ...
]
```

---

### 5. **GET `/crop-economics/api/top-crops`**

**Purpose:** Get top 5 oilseeds by market activity

**Authentication:** Required

**Response Format:**
```json
[
  {
    "name": "Groundnut",
    "listings": 12,
    "icon": "🫘",
    "price": 7400.00
  },
  ...
]
```

---

### 6. **GET `/crop-economics/api/market-details/<crop>`**

**Purpose:** Get detailed market-wise price information

**Authentication:** Required

**Parameters:**
- `crop`: Crop key (e.g., 'soybean')

**Response Format:**
```json
{
  "crop": "Soybean",
  "total_markets": 8,
  "markets": [
    {
      "price": 5800.00,
      "market": "Indore Mandi",
      "state": "Madhya Pradesh",
      "date": "2024-12-09",
      "min_price": 5500.00,
      "max_price": 6000.00
    },
    ...
  ],
  "source": "Government API - data.gov.in"
}
```

---

### 7. **GET `/crop-economics/api/debug`**

**Purpose:** Test API connectivity (for debugging)

**Authentication:** Not required

**Response:** Shows API status and sample data

---

## 🎨 Frontend Implementation

### File: `templates/crop_economics.html`

#### 1. **Page Structure**

```html
<!-- Navigation Tabs -->
<div class="nav-tabs">
  <button onclick="switchTab('live-prices')">📊 Live Prices</button>
  <button onclick="switchTab('comparison')">📈 Comparison Chart</button>
  <button onclick="switchTab('market-details')">🏪 Market Details</button>
</div>

<!-- Tab Contents -->
<div id="live-prices-tab">
  <!-- Price cards grid -->
</div>

<div id="comparison-tab">
  <!-- Comparison bar chart -->
</div>

<!-- Crop Details Modal -->
<div id="cropModal" class="modal-overlay">
  <div class="modal-panel">
    <!-- Crop info and price history chart -->
  </div>
</div>
```

#### 2. **Key JavaScript Functions**

##### `loadPrices()`

**Purpose:** Fetch and display live oilseed prices

**Process:**
1. Calls `/crop-economics/api/prices`
2. Iterates through each crop
3. Creates price card HTML
4. Displays in grid layout
5. Adds click handler to open crop details

**HTML Generated:**
```html
<div class="price-card" onclick="showCropDetails('soybean')">
  <div class="card-icon">🫘</div>
  <div class="card-name">Soybean</div>
  <div class="card-price">₹5500</div>
  <div class="card-meta">8 markets</div>
</div>
```

---

##### `showCropDetails(cropKey)`

**Purpose:** Open modal with crop details and price history chart

**Process:**
1. Fetch crop data from `/crop-economics/api/prices`
2. Populate modal fields:
   - Icon and name
   - Average, min, max prices
   - Number of listings
   - Price trend indicator
3. Open modal
4. Call `loadPriceHistoryChart(cropKey)`

**Modal Fields:**
```
┌─────────────────────────────────┐
│ 🫘 Soybean                  [X] │
├─────────────────────────────────┤
│ Average: ₹5500                  │
│ Max: ₹6000  |  Min: ₹5200       │
│ Markets: 8                      │
│ Trend: ↑ Rising                 │
│                                 │
│ [6-Month Price History Chart]   │
├─────────────────────────────────┤
│ [Close]  [View Buyers]          │
└─────────────────────────────────┘
```

---

##### `loadPriceHistoryChart(cropKey)`

**Purpose:** Fetch and render 12-month price trend bar chart

**Process:**
1. Calls `/crop-economics/api/price-history/{cropKey}`
2. Receives monthly history data
3. Creates/removes chart container
4. Initializes Chart.js bar chart
5. Sets up responsive sizing

**Chart Configuration:**
```javascript
{
  type: 'bar',
  data: {
    labels: ['Dec 2024', 'Nov 2024', ..., 'Jan 2024'],
    datasets: [{
      label: 'Average Price (₹)',
      data: [5500, 5470, 5440, ...],
      backgroundColor: '#4CAF50',
      borderColor: '#2E7D32'
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    // Y-axis shows rupees
    // X-axis shows months
  }
}
```

---

##### `loadComparisonChart()`

**Purpose:** Fetch and display price comparison bar chart

**Process:**
1. Calls `/crop-economics/api/comparison`
2. Sorts crops by price (highest first)
3. Creates Chart.js bar chart
4. Shows all 7 oilseeds side-by-side

**Chart Shows:**
- X-axis: Crop names
- Y-axis: Prices in rupees
- Colors: Green for better visualization

---

#### 3. **CSS Styling**

**Key Classes:**
```css
.price-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
.price-card { background: white; border-radius: 8px; padding: 15px; text-align: center; cursor: pointer; }
.price-card:hover { background: #f5f5f5; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); }
.modal-panel { background: white; border-radius: 8px; padding: 20px; max-width: 600px; margin: 50px auto; }
.chart-container { height: 300px; background: white; border-radius: 8px; padding: 12px; }
```

---

## 📊 Data Models

### MarketPrice Table (Database)

```python
class MarketPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commodity_name = db.Column(db.String(100))
    market_name = db.Column(db.String(100))
    market_state = db.Column(db.String(50))
    open_price = db.Column(db.Float)
    close_price = db.Column(db.Float)
    high_price = db.Column(db.Float)
    low_price = db.Column(db.Float)
    volume = db.Column(db.Integer)
    price_date = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.now)
```

**Used For:** Fallback price data when government API is unavailable

---

## 🔄 Data Flow Examples

### Example 1: User Opens Dashboard

```
1. User navigates to /crop-economics/dashboard
2. Flask returns HTML page
3. JavaScript loads and calls loadPrices()
4. Frontend fetches GET /crop-economics/api/prices
5. Backend:
   - Loops through 7 oilseeds
   - For each crop, calls fetch_live_prices_from_api()
   - Tries Government API → DB → Mock Data
   - Calculates avg, min, max prices
   - Returns JSON with all crop data
6. Frontend renders 7 price cards in grid
7. User sees live prices from multiple markets
```

### Example 2: User Clicks on Soybean

```
1. User clicks "Soybean" price card
2. showCropDetails('soybean') is called
3. Frontend:
   - Fetches /crop-economics/api/prices (already cached)
   - Populates modal with soybean data
   - Opens modal
   - Calls loadPriceHistoryChart('soybean')
4. loadPriceHistoryChart:
   - Fetches /crop-economics/api/price-history/soybean
   - Receives 12 months of data
   - Initializes Chart.js bar chart
   - Renders chart in modal
5. User sees:
   - Current price statistics
   - 12-month price trend graph
   - Price movement visualization
```

---

## 🔐 Security Features

1. **Authentication:** All endpoints require login (except debug)
2. **Session Management:** Uses Flask session for user verification
3. **Input Validation:** Crop keys validated against OILSEEDS dictionary
4. **Error Handling:** Graceful fallbacks prevent crashes
5. **Timeout Protection:** API requests have 10-second timeout

---

## 📈 Performance Considerations

1. **Caching Strategy:**
   - Frontend caches price data during session
   - Avoids redundant API calls
   - Chart.js destroys old charts to prevent memory leaks

2. **Database Optimization:**
   - Queries limit results (50 records max)
   - Indexes on commodity_name and updated_at recommended

3. **Mock Data:**
   - Used for demo to avoid 3rd-party API delays
   - Generated on-the-fly (no persistence)

---

## 🐛 Troubleshooting

### Issue: "Failed to load price history"

**Cause:** API endpoint not returning data  
**Solution:** Check that crop name matches OILSEEDS dictionary keys

### Issue: All months showing same name

**Cause:** Incorrect month calculation  
**Solution:** Ensure `dateutil` package is installed and imported

### Issue: Chart not displaying

**Cause:** Canvas element not found or Chart.js not loaded  
**Solution:** Check browser console for errors; verify Chart.js is loaded in base template

### Issue: Government API returning 0 records

**Cause:** API key invalid or commodity name mismatch  
**Solution:** Use debug endpoint to test; check OILSEEDS 'api_name' mappings

---

## 🚀 Future Enhancements

1. **Real-time Updates:**
   - WebSocket integration for live price updates
   - Refresh prices every 5 minutes

2. **Price Alerts:**
   - Notify farmers when price drops/rises by threshold
   - Email/SMS alerts

3. **Advanced Analytics:**
   - Price forecasting using ML
   - Seasonal trends analysis
   - Market correlation matrix

4. **Export Features:**
   - Download price data as CSV/Excel
   - Generate PDF reports

5. **Multi-language Support:**
   - Hindi translations for all labels
   - Regional language support

6. **Mobile Optimization:**
   - Responsive chart sizing
   - Touch-friendly controls
   - Offline mode

---

## 📞 Support & Maintenance

**API Provider:** Ministry of Agriculture & Farmers Welfare, Government of India  
**Dataset URL:** https://data.gov.in/resource/9ef84268-d588-465a-a5c3-375cda092f58  
**Last Updated:** December 9, 2025  
**Maintained By:** TelhanSathi Development Team

---

## 📝 Code Statistics

- **Backend File:** routes/crop_economics.py (386 lines)
- **Frontend File:** templates/crop_economics.html (1014 lines)
- **API Endpoints:** 7 routes
- **Supported Oilseeds:** 7 varieties
- **Database Tables:** MarketPrice
- **JavaScript Libraries:** Chart.js
- **Data Sources:** Government API + Database + Mock Data

---

## 🎯 Key Metrics

| Metric | Value |
|--------|-------|
| API Response Time | < 5 seconds |
| Fallback Options | 3 (API → DB → Mock) |
| Historical Data | 12 months |
| Supported Crops | 7 oilseeds |
| Markets Per Crop | 6-10+ |
| Chart Types | Bar, Trend |
| Mobile Responsive | Yes |
| Authentication | Yes |

---

**End of Documentation**
