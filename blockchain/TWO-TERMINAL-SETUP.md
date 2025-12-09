# 🚀 Two-Terminal Node Setup Guide

This guide shows how to run a blockchain node with ngrok tunnel using **2 separate terminals**.

## Why Two Terminals?

- **Terminal 1:** Runs the ngrok tunnel (shows you the public URL)
- **Terminal 2:** Runs the blockchain node (connects to the tunnel)

This gives you more control and lets you see what's happening in each process.

---

## ⚠️ Prerequisites (One-Time Setup)

### 1. Get ngrok Auth Token
1. Go to: https://dashboard.ngrok.com
2. Sign up or login
3. Copy your **Auth Token** (looks like: `2abc_xyz123...`)
4. Add it to `.env` file:
   ```
   NGROK_AUTH_TOKEN=your_token_here
   ```

### 2. Check Node.js is Installed
```bash
node --version
# Should show: v18+ or higher
```

### 3. Install Dependencies
```bash
npm install
```

---

## 🎯 Quick Start (2 Terminals)

### Terminal 1: Start ngrok Tunnel

**Open PowerShell in the blockchain folder:**
```bash
cd "c:\Users\Harsh Pandhe\Desktop\SIH\blockchain"
.\start-ngrok-tunnel.ps1
```

**You should see:**
```
🌐 TelhanSathi Blockchain - ngrok Tunnel
========================================

✅ ngrok found at: C:\ProgramData\chocolatey\bin\ngrok.exe

📋 Configuration:
   Local Port: 3010
   ngrok Region: in

🔐 Authenticating with ngrok...
✅ Authentication successful!

🚀 Starting ngrok tunnel...
   Exposing: http://localhost:3010

Session Status                online
Account                       yourname@email.com
Version                       3.x.x
Region                        India (in)
Latency                       xx ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://aaaa-bbbb-cccc.ngrok.io -> http://localhost:3010

Command Line Options           http_proxy=http://127.0.0.1:4040

Press CTRL+C to quit
```

**⚠️ IMPORTANT: Copy the public URL from ngrok output**
```
https://aaaa-bbbb-cccc.ngrok.io
```
You'll need this URL to connect other nodes.

**Keep this terminal running!** ✅

---

### Terminal 2: Start Blockchain Node

**Open a NEW PowerShell window in the same folder:**
```bash
cd "c:\Users\Harsh Pandhe\Desktop\SIH\blockchain"
.\start-node-only.ps1
```

**You should see:**
```
🚀 TelhanSathi Blockchain - Node 1
========================================

✅ Node.js version: v24.6.0

📋 Checking dependencies...
✅ All dependencies present

📋 Configuration:
   Node ID: node1
   HTTP Port: 3010
   P2P Port: 6001

💡 IMPORTANT:
   Make sure ngrok tunnel is running in ANOTHER terminal:
   > .\start-ngrok-tunnel.ps1

🚀 Starting blockchain node...

🔥 Firebase REST API initialized!
   Database: https://sih2025-72065-default-rtdb.asia-southeast1.firebasedatabase.app

🚀 Initializing TelhanSathi Blockchain...
   Node ID: node1
   HTTP Port: 3000
   P2P Port: 6001
   Distributed Mode: ENABLED

============================================================
🌾 TelhanSathi Agricultural Blockchain Network
============================================================
📡 Server running on: http://localhost:3010

📊 Web Dashboard Endpoints:
   POST /transaction/add    - Add new transaction
   GET  /chain              - View entire blockchain
   GET  /stats              - Blockchain statistics
   ...

📱 Mobile App API Endpoints:
   GET  /api/health         - System health check
   GET  /api/mobile/transactions?userId=xxx
   ...

✅ Blockchain initialized successfully
```

**Node is now running!** ✅

---

## 📱 Verify Both Are Working

### Test 1: Check Node Health (Terminal 2)
In a third PowerShell window, run:
```bash
curl http://localhost:3010/api/health
```

Should return:
```json
{
  "status": "healthy",
  "node": {
    "nodeId": "node1",
    "publicUrl": "https://aaaa-bbbb-cccc.ngrok.io"
  }
}
```

### Test 2: Check ngrok Tunnel Status
Open your browser and go to:
```
http://localhost:4040
```

You'll see:
- Requests being tunneled
- HTTP status codes
- Request/response details

---

## 🖥️ Multi-PC Setup

### PC 2 Setup (Another Computer)

**On PC 2:**

#### Terminal 1 (PC 2): Start ngrok Tunnel
```bash
.\start-ngrok-tunnel.ps1
```

Get the URL:
```
https://xxxx-yyyy-zzzz.ngrok.io
```

#### Terminal 2 (PC 2): Start Node
Before running the node, update `.env` to connect to PC 1:
```env
NODE_ID=node2
PORT=3010
P2P_PORT=6002
BOOTSTRAP_NODES=https://aaaa-bbbb-cccc.ngrok.io,node1
```

Then run:
```bash
.\start-node-only.ps1
```

---

## 📊 Share URLs Between PCs

| PC | Terminal 1 (ngrok) | Terminal 2 (Node) | Public URL |
|----|-------------------|------------------|------------|
| PC 1 | `start-ngrok-tunnel.ps1` | `start-node-only.ps1` | https://aaaa-bbbb-cccc.ngrok.io |
| PC 2 | `start-ngrok-tunnel.ps1` | `start-node-only.ps1` | https://xxxx-yyyy-zzzz.ngrok.io |
| PC 3 | `start-ngrok-tunnel.ps1` | `start-node-only.ps1` | https://wwww-pppp-mmmm.ngrok.io |

**To connect PC 2 to PC 1:**
1. Get PC 1's ngrok URL: `https://aaaa-bbbb-cccc.ngrok.io`
2. Add to PC 2's `.env`: `BOOTSTRAP_NODES=https://aaaa-bbbb-cccc.ngrok.io,node1`
3. Start PC 2's node
4. Nodes will auto-sync!

---

## 🔍 Troubleshooting

### Problem: "ngrok not found"
```bash
# Install ngrok
npm install -g ngrok
# OR
choco install ngrok
# OR download from https://ngrok.com
```

### Problem: "NGROK_AUTH_TOKEN not set"
1. Open `.env` file
2. Add: `NGROK_AUTH_TOKEN=your_token_from_dashboard`
3. Save
4. Try again

### Problem: "Cannot connect to bootstrap node"
1. Make sure PC 1's ngrok tunnel is RUNNING
2. Make sure ngrok URL is correct in PC 2's `.env`
3. Verify URL works: Open in browser

### Problem: "Port 3010 already in use"
```bash
# Find process using port
netstat -ano | findstr :3010

# Kill it (replace PID with actual PID)
taskkill /PID <PID> /F
```

### Problem: "Firebase connection error"
- Check internet connection
- Firebase might be down (check status at https://status.firebase.google.com)
- Wait a minute and try again

---

## 📝 Terminal 1 vs Terminal 2

### Terminal 1 (ngrok)
```
🌐 TelhanSathi Blockchain - ngrok Tunnel
✅ Authentication successful!
🚀 Starting ngrok tunnel...
Forwarding: https://aaaa-bbbb-cccc.ngrok.io -> http://localhost:3010
```

**What to do:** Keep running, copy the public URL

### Terminal 2 (Node)
```
🚀 TelhanSathi Blockchain - Node 1
✅ Node.js version: v24.6.0
✅ All dependencies present
🚀 Starting blockchain node...
✅ Blockchain initialized successfully
```

**What to do:** Keep running, it's your node!

---

## 🔄 How It Works Together

```
Terminal 1 (ngrok)
├─ Exposes localhost:3010 to the internet
├─ Creates tunnel: https://aaaa-bbbb-cccc.ngrok.io
└─ Forwards public requests to your node

       ↓↓↓ HTTP Traffic ↓↓↓

Terminal 2 (Node)
├─ Runs on localhost:3010
├─ Receives requests from ngrok tunnel
├─ Connects to Firebase
├─ Syncs with other nodes
└─ Stores blockchain data
```

---

## 📱 Connect Mobile App

Once both terminals are running:

```javascript
// Use the ngrok URL from Terminal 1
const BLOCKCHAIN_URL = 'https://aaaa-bbbb-cccc.ngrok.io';

// Send transaction
fetch(`${BLOCKCHAIN_URL}/api/mobile/transaction/send`, {
  method: 'POST',
  body: JSON.stringify({
    from: 'farmer1',
    to: 'buyer1',
    amount: 100
  })
});
```

---

## ✅ Checklist

- [ ] ngrok installed and working
- [ ] ngrok auth token in .env
- [ ] Node.js v18+ installed
- [ ] npm dependencies installed (`npm install`)
- [ ] Terminal 1: ngrok tunnel running
- [ ] Terminal 2: blockchain node running
- [ ] Can access http://localhost:4040 (ngrok status)
- [ ] Can access http://localhost:3010/api/health (node health)
- [ ] Have copied ngrok public URL
- [ ] Ready to connect other PCs!

---

## 🚀 Next Steps

1. **Single PC Testing:** Run both terminals on this PC
2. **Multi-PC Setup:** Share ngrok URL with other PCs
3. **Mobile App:** Connect mobile to blockchain_url
4. **Production:** Deploy on actual servers or different machines

---

**That's it! You now have a public blockchain accessible from anywhere!** 🎉
