const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const os = require('os');

const app = express();
const PORT = 3000;
const DB_FILE = 'database.json';

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// --- DATA PERSISTENCE FUNCTIONS ---

// Load data from local JSON file (prevents data loss on restart)
function loadData() {
    if (fs.existsSync(DB_FILE)) {
        try {
            const rawData = fs.readFileSync(DB_FILE);
            return JSON.parse(rawData);
        } catch (error) {
            console.error("Error reading database file, starting fresh.");
            return { current: {}, history: [] };
        }
    }
    return { current: {}, history: [] };
}

// Save data to local JSON file
function saveData(data) {
    // Limit history to last 100 points to keep file size manageable
    if (data.history.length > 100) {
        data.history = data.history.slice(-100);
    }
    fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2));
}

// Initialize Data
let db = loadData();

// --- HELPER FUNCTIONS ---
function formatTimestamp(date) {
    return date.toLocaleTimeString('en-US', { hour12: false });
}

function getLocalIp() {
    const nets = os.networkInterfaces();
    for (const name of Object.keys(nets)) {
        for (const net of nets[name]) {
            if (net.family === 'IPv4' && !net.internal) {
                return net.address;
            }
        }
    }
    return 'localhost';
}

// --- ROUTES ---

// 1. Endpoint for ESP32 to POST data
app.post('/api/update', (req, res) => {
    const rawData = req.body;

    // Basic validation
    if (!rawData) {
        console.log('[WARN] Received empty data');
        return res.sendStatus(400);
    }

    const now = new Date();

    // Parse and sanitize incoming data
    const newData = {
        airTemp: parseFloat(rawData.airTemp) || 0,
        airHum: parseFloat(rawData.airHum) || 0,
        heatIndex: parseFloat(rawData.heatIndex) || 0,
        soilTemp: parseFloat(rawData.soilTemp) || 0,
        soilMoist: parseInt(rawData.soilMoist) || 0,
        soilRaw: parseInt(rawData.soilRaw) || 0,       // Debugging
        light: parseFloat(rawData.light) || 0,         // Lux Value
        lightRaw: parseInt(rawData.lightRaw) || 0,     // ADC Value
        rssi: parseInt(rawData.rssi) || 0,
        uptime: parseInt(rawData.uptime) || 0,
        timestamp: formatTimestamp(now),
        fullDate: now.toISOString()
    };

    // Update Memory
    db.current = newData;
    db.history.push(newData);

    // Save to File (Local Storage)
    saveData(db);

    console.log(`[DATA] Lux: ${newData.light.toFixed(1)} | Moisture: ${newData.soilMoist}% | Temp: ${newData.airTemp.toFixed(1)}°C`);
    res.json({ status: 'success' });
});

// 2. Endpoint for Frontend to GET data
app.get('/api/data', (req, res) => {
    res.json(db);
});

// 3. Reset Data Endpoint (Clears history)
app.post('/api/reset', (req, res) => {
    db = { current: {}, history: [] };
    saveData(db);
    console.log('[RESET] Database cleared by user.');
    res.json({ status: 'cleared' });
});

// Start Server
app.listen(PORT, '0.0.0.0', () => {
    const ip = getLocalIp();
    console.log(`-----------------------------------------------`);
    console.log(`🌱 SMART GARDEN SERVER RUNNING`);
    console.log(`📂 Storage:   ${path.join(__dirname, DB_FILE)}`);
    console.log(`💻 Dashboard: http://localhost:${PORT}`);
    console.log(`📡 ESP32 URL: http://${ip}:${PORT}/api/update`);
    console.log(`-----------------------------------------------`);
}); 