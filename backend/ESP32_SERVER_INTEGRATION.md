# ESP32 Server Integration - Data Flow Documentation

## ESP32 Payload Structure

Your ESP32 sends the following JSON payload to **`http://<server-ip>:3000/api/update`**:

```json
{
  "airTemp": 28.5,           // °C - DHT22 ambient temperature
  "airHum": 65.3,            // % - DHT22 humidity
  "heatIndex": 30.2,         // °C - Computed heat index/feel-like temp
  "soilTemp": 22.1,          // °C - DS18B20 soil temperature probe
  "soilMoist": 45,           // % - Soil moisture percentage (mapped from dryVal-wetVal)
  "soilRaw": 2145,           // 0-4095 - Raw ADC value of soil sensor
  "light": 1200.5,           // Lux - Calculated light intensity
  "lightRaw": 2800,          // 0-4095 - Raw ADC value of light sensor
  "rssi": -65,               // dBm - WiFi signal strength
  "uptime": 3600             // seconds - Device uptime
}
```

## Server Endpoints

### Primary Endpoint: `/field-monitoring/api/update` (or `/field-monitoring/api/push`)

**Request:**
- **Method:** POST
- **Content-Type:** application/json
- **URL:** `http://<server-ip>:3000/field-monitoring/api/update`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Data received and stored",
  "reading_id": "uuid-string",
  "device_serial": "192.168.x.x"
}
```

## Data Mapping (ESP32 → Database)

The server automatically maps ESP32 field names to database fields:

| ESP32 Field | Database Field | Type | Unit | Description |
|-------------|----------------|------|------|-------------|
| `airTemp` | `temperature` | Float | °C | Ambient air temperature |
| `airHum` | `humidity` | Float | % | Air humidity |
| `heatIndex` | `heat_index` | Float | °C | Heat index (feel-like temperature) |
| `soilMoist` | `soil_moisture` | Float | % | Soil moisture percentage |
| `soilRaw` | `soil_raw` | Integer | 0-4095 | Raw ADC value of soil sensor |
| `soilTemp` | `soil_temp` | Float | °C | Soil temperature from DS18B20 |
| `light` | `light` | Float | Lux | Calculated light intensity |
| `lightRaw` | `light_raw` | Integer | 0-4095 | Raw ADC value of light sensor |
| `rssi` | `rssi` | Integer | dBm | WiFi signal strength |
| `uptime` | `uptime` | Integer | seconds | Device uptime |

## Database Storage

Each reading is stored in the `sensor_readings` table with:

- **device_id**: Auto-detected from ESP32's IP address on first connection
- **received_at**: Server timestamp when data arrived
- All 10 sensor fields preserved exactly as sent

### Auto-Device Creation

On first connection:
1. Server checks if device exists by IP address
2. If not, creates new `IoTDevice` record with:
   - `device_serial`: ESP32's IP address (e.g., "192.168.1.150")
   - `farmer_id`: Default = 1 (update later via admin)
   - `is_active`: True
   - `installed_at`: Current timestamp
   - `last_seen`: Updated with each data push

## Frontend Retrieval

The dashboard fetches data from `/field-monitoring/api/readings`:

```json
{
  "device": {
    "id": "device-uuid",
    "serial": "192.168.x.x"
  },
  "readings": [
    {
      "temperature": 28.5,
      "humidity": 65.3,
      "heat_index": 30.2,
      "soil_moisture": 45,
      "soil_raw": 2145,
      "soil_temp": 22.1,
      "light": 1200.5,
      "light_raw": 2800,
      "rssi": -65,
      "uptime": 3600,
      "received_at": "2025-12-09T10:30:45.123456"
    }
    // ... up to 48 most recent readings
  ],
  "field_status": {
    "overall_status": "Good",
    "status_color": "#22c55e",
    "metrics": {...},
    "recommendations": [...]
  }
}
```

## Configuration Steps

### On ESP32:

1. Power on ESP32
2. If not configured, it starts Access Point mode:
   - SSID: `SmartGarden-Setup`
   - Password: `12345678`
3. Connect to AP and navigate to `192.168.4.1`
4. Enter:
   - WiFi SSID: Your home/office network
   - WiFi Password: Network password
   - Server IP: Your server's IP (e.g., `192.168.1.5`)
5. Click "Save & Restart"

### On Server:

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# (Optional) Update device's farmer_id
# SQL: UPDATE iot_devices SET farmer_id = '<correct_id>' WHERE device_serial = '<ip>'

# Start Flask server
python app.py
# or
flask run --host=0.0.0.0 --port=3000
```

### On Dashboard:

1. Login as farmer
2. Navigate to `/field-monitoring/device-control`
3. View live sensor readings and 48-hour trend charts

## Verification

To verify data flow:

1. **Check server console** for:
   ```
   Data Sent. LUX: 1200.5 | Soil: 45
   ```

2. **Check database** (SQLite):
   ```bash
   sqlite3 instance/app.db
   SELECT * FROM sensor_readings ORDER BY received_at DESC LIMIT 1;
   ```

3. **Check API response**:
   ```bash
   curl http://localhost:3000/field-monitoring/api/readings
   ```

4. **Check dashboard** at:
   ```
   http://localhost:3000/field-monitoring/device-control
   ```

## All Supported Field Names

The server accepts both ESP32 style and alternative field names:

```python
temperature:    'airTemp' OR 'temperature'
humidity:       'airHum' OR 'humidity'
heat_index:     'heatIndex' OR 'heat_index'
soil_moisture:  'soilMoist' OR 'soil_moisture'
soil_raw:       'soilRaw' OR 'soil_raw'
soil_temp:      'soilTemp' OR 'probe_temp'
light:          'light'
light_raw:      'lightRaw' OR 'light_raw'
rssi:           'rssi'
uptime:         'uptime'
```

## Database Schema

**sensor_readings table:**
- id (UUID, primary key)
- device_id (foreign key)
- temperature (Float)
- humidity (Float)
- heat_index (Float) ✨ NEW
- soil_moisture (Float)
- soil_raw (Integer) ✨ NEW
- soil_temp (Float)
- light (Float)
- light_raw (Integer)
- rssi (Integer)
- uptime (Integer)
- received_at (DateTime, indexed)

**iot_devices table:**
- id, farmer_id, device_serial, device_mac, device_name
- is_active, last_seen, wifi_ssid, firmware_version
- calibration values (soil_dry_value, soil_wet_value)
- timestamps (created_at, updated_at, installed_at)

## Troubleshooting

### ESP32 shows "Failed to connect"
- Verify WiFi SSID and password
- Check server IP is correct and reachable
- Press BOOT button for 2 seconds to reset config and reconfigure

### Server returns 404
- Ensure endpoint is `/field-monitoring/api/update` (not just `/api/update`)
- Check server is running on correct port (3000 by default)

### No data appearing in dashboard
- Verify ESP32 is connected to WiFi (check Serial output)
- Check database has `iot_devices` record (farmer_id might be 1 by default)
- Login as correct farmer account

### Charts not updating
- Ensure database is populated (check SQLite directly)
- Refresh browser (F5)
- Check browser console for JavaScript errors

## Migration Status

Latest applied migration: **iot_enhancements_002 (head)**

- iot_enhancements_001: Initial IoT fields
- iot_enhancements_002: Added heat_index and soil_raw fields

All fields are now supported and stored in the database.
