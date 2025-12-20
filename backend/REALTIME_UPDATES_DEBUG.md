# Real-Time Data Update Troubleshooting Guide

## ✅ What We Fixed

1. **API Endpoint**: Updated `/api/push` to properly commit device updates to database
2. **Frontend Polling**: Reduced refresh interval from 10 seconds → 3 seconds for real-time updates
3. **Smart Update Detection**: Frontend now only updates UI when NEW data arrives (timestamp comparison)
4. **Detailed Logging**: Added console and server logs to track data flow

## 🔍 How to Debug Real-Time Updates

### Step 1: Check Server Logs (Flask Console)

Run Flask in a terminal and watch for incoming ESP32 requests:

```bash
cd backend
.\.venv\Scripts\Activate.ps1
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development"
python app.py
```

**Look for output like:**
```
=== ESP32 DATA RECEIVED ===
Device ID: 192.168.1.150
Timestamp: 2025-12-09 10:30:45.123456
Payload: {'airTemp': 28.5, 'airHum': 65.3, ...}
✓ Found existing device: uuid-xxx
✓ Updated device last_seen
✓ Stored reading: uuid-yyy
  Temp: 28.5°C, Humidity: 65.3%, Soil: 45%
  Light: 1200 lux, RSSI: -65 dBm
=========================
```

### Step 2: Check Browser Console (Frontend)

1. Open dashboard: `http://localhost:3000/field-monitoring/device-control`
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Watch for output like:

```
🔄 Starting auto-refresh every 3000ms
✓ New data received at 10:30:45 {temperature: 28.5, humidity: 65.3, ...}
✓ New data received at 10:30:48 {temperature: 28.6, humidity: 65.1, ...}
⏳ Waiting for new data...  (if timestamp hasn't changed)
```

### Step 3: Check Network Tab

1. Open DevTools → **Network** tab
2. Filter for "readings"
3. Watch requests to `/field-monitoring/api/readings`
4. Check **Response** shows new data each time:

```json
{
  "device": {"id": "...", "serial": "192.168.1.150"},
  "readings": [
    {
      "temperature": 28.5,
      "humidity": 65.3,
      "received_at": "2025-12-09T10:30:45.123456"
    }
  ]
}
```

## 🔧 Troubleshooting Checklist

### Issue: No requests reaching server

**Symptoms:**
- Server console shows no logs
- "Waiting for sensor data from ESP32" message stays

**Causes & Fixes:**
1. **Wrong server IP in ESP32 code**
   - ESP32 sends to: `http://<config_server>:3000/api/update`
   - Verify IP is correct: `ping <server-ip>`
   - Verify port 3000 is open: Check firewall

2. **WiFi connection issue**
   - Check Serial output on ESP32: Should see "WiFi Connected!"
   - If not, press BOOT button 2 seconds to reset config
   - Reconfigure with correct SSID/password

3. **Endpoint path wrong**
   - ESP32 code sends to: `/api/update` ✅
   - Server accepts: `/api/update` OR `/api/push` ✅
   - Should work!

### Issue: Requests received, but only once

**Symptoms:**
- Server shows one request, then no more
- ESP32 Serial shows only one "Data Sent" message

**Causes & Fixes:**
1. **ESP32 loop() has long delays**
   - Check Arduino code: `delay(3000)` is okay
   - If you see `delay(30000)` or more, reduce it
   - Data should push every 3 seconds

2. **ESP32 crashes after first send**
   - Watch Serial monitor for error messages
   - Common: Stack overflow, memory issues
   - Solution: Reduce sensor averaging loop iterations

3. **Network connection drops**
   - Add WiFi reconnection logic in ESP32 code:
   ```cpp
   if(WiFi.status() != WL_CONNECTED) {
       Serial.println("Reconnecting WiFi...");
       WiFi.reconnect();
       delay(5000);
   }
   ```

### Issue: Requests come in, but frontend doesn't update

**Symptoms:**
- Server logs show data arriving
- Browser shows "Data received ✅" but values don't change
- Charts show old data only

**Causes & Fixes:**
1. **Timestamp comparison issue**
   - Check browser console for "⏳ Waiting for new data..." spam
   - Means data is arriving but timestamp hasn't changed
   - Cause: ESP32 sending same timestamp for multiple readings
   - Solution: Ensure `received_at` uses server timestamp (automatic in current code)

2. **Database not saving correctly**
   - Run SQL query:
   ```bash
   sqlite3 instance/app.db
   SELECT id, received_at, temperature FROM sensor_readings ORDER BY received_at DESC LIMIT 5;
   ```
   - Should show new timestamps every 3 seconds
   - If not, issue is in `/api/push` endpoint

3. **Frontend not polling regularly**
   - Browser console should show new "✓ Data received" every 3 seconds
   - If not, check:
     - Is auto-refresh running? Look for "🔄 Starting auto-refresh"
     - Are there JavaScript errors? Check console for red errors
     - Is page in background? Browser throttles requests (switch to tab)

## 📊 Expected Data Flow

```
ESP32 (every 3 seconds)
  ↓
  POST to http://<server>:3000/api/update with JSON payload
  ↓
Server `/api/push` endpoint
  ↓
  Creates/updates IoTDevice record
  ↓
  Stores SensorReading in database
  ↓
  Returns 200 OK
  ↓
Frontend (every 3 seconds)
  ↓
  GET /api/readings
  ↓
  Checks if timestamp changed
  ↓
  Updates UI with new values
  ↓
  Updates charts with all 48 readings
  ↓
  Shows "Data updated ✅" status
```

## 📝 Database Verification

Check if data is actually being stored:

```bash
# Connect to SQLite database
sqlite3 instance/app.db

# Check device
SELECT id, device_serial, farmer_id, last_seen FROM iot_devices;

# Check readings (should show increasing timestamps)
SELECT temperature, humidity, soil_moisture, light, rssi, received_at 
FROM sensor_readings 
ORDER BY received_at DESC 
LIMIT 10;

# Check reading count per device
SELECT device_id, COUNT(*) as reading_count, MAX(received_at) as latest
FROM sensor_readings
GROUP BY device_id;
```

## 🔄 Real-Time Update Architecture

**3-Second Loop:**

1. **00:00** - ESP32 sends data → Server stores in DB
2. **00:03** - Frontend polls `/api/readings` → Gets latest
3. **00:06** - Frontend polls again → Gets new data if ESP32 sent
4. **00:09** - Continue...

**Why 3 seconds?**
- Fast enough to feel "real-time" for farmer
- Slow enough to not overload database
- Matches ESP32 send interval

## ✨ Optimization Tips

If you want even faster updates:

1. **Reduce refresh interval** (frontend):
   ```javascript
   this.refreshRate = 2000; // 2 seconds
   ```

2. **Reduce ESP32 send interval** (Arduino):
   ```cpp
   delay(2000); // Send every 2 seconds instead of 3
   ```

3. **Use WebSocket** (advanced):
   - Replaces polling with push notifications
   - Server pushes new data to all connected clients instantly
   - More complex but best real-time experience

## 🧪 Manual Testing

### Test 1: Simulate ESP32 data with curl

```bash
# Send test data to server
curl -X POST http://localhost:3000/field-monitoring/api/update \
  -H "Content-Type: application/json" \
  -d '{
    "airTemp": 28.5,
    "airHum": 65.3,
    "heatIndex": 30.2,
    "soilTemp": 22.1,
    "soilMoist": 45,
    "soilRaw": 2145,
    "light": 1200,
    "lightRaw": 2800,
    "rssi": -65,
    "uptime": 3600
  }'
```

**Expected response:**
```json
{
  "success": true,
  "message": "Data received and stored",
  "reading_id": "uuid",
  "device_serial": "127.0.0.1",
  "timestamp": "2025-12-09T10:30:45.123456"
}
```

### Test 2: Check API returns data

```bash
curl http://localhost:3000/field-monitoring/api/readings
```

Should return array of readings with latest first.

### Test 3: Monitor database in real-time

```bash
# Run this in loop to watch database update every 3 seconds
watch -n 1 "sqlite3 instance/app.db 'SELECT temperature, humidity, received_at FROM sensor_readings ORDER BY received_at DESC LIMIT 1;'"
```

## 📱 Quick Checklist

- [ ] Flask server running and shows logs
- [ ] ESP32 shows "WiFi Connected!" in Serial
- [ ] Server logs show "=== ESP32 DATA RECEIVED ===" messages
- [ ] Browser console shows "✓ New data received" messages every 3 seconds
- [ ] Dashboard values update with new numbers every 3 seconds
- [ ] Charts show new points every 3 seconds
- [ ] Database query shows increasing timestamps in `received_at`

If all checks pass, **real-time updates are working!** 🎉

## 🆘 Still Not Working?

1. **Share server console output** (first 10 lines when ESP32 sends data)
2. **Share browser console errors** (screenshot or copy-paste red errors)
3. **Share database query result** (last 5 readings)
4. **ESP32 Serial output** (connection and send messages)

This will help diagnose the exact issue!
