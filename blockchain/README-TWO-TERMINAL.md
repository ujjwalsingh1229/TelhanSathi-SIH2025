# 🚀 TelhanSathi Blockchain - Two-Terminal Setup

## 🎯 What This Is

A **simple, clean blockchain node setup** using two separate terminals:
- **Terminal 1:** ngrok tunnel (public access)
- **Terminal 2:** Blockchain node (your application)

## ⚡ Quick Start (3 Steps)

### Step 1: Prepare
```bash
# Get ngrok token from: https://dashboard.ngrok.com
# Add to .env: NGROK_AUTH_TOKEN=your_token
npm install
```

### Step 2: Terminal 1 - ngrok Tunnel
```powershell
.\start-ngrok-tunnel.ps1
```

**Copy the URL you see:**
```
https://aaaa-bbbb-cccc.ngrok.io
```

**Keep this terminal OPEN!**

### Step 3: Terminal 2 - Blockchain Node
```powershell
.\start-node-only.ps1
```

**Done!** Your node is running. ✅

---

## 🧪 Test It

```bash
# In a 3rd terminal
curl http://localhost:3010/api/health
```

Should return:
```json
{ "status": "healthy", "node": { "nodeId": "node1" } }
```

---

## 🖥️ Multi-PC Setup

### On PC 1 (this computer)
1. Run both startup scripts (as above)
2. Copy ngrok URL from Terminal 1

### On PC 2 (another computer)
1. Copy the entire `blockchain` folder
2. Edit `.env` and add:
   ```env
   BOOTSTRAP_NODES=https://aaaa-bbbb-cccc.ngrok.io,node1
   ```
3. Run both startup scripts:
   - Terminal 1: `.\start-ngrok-tunnel.ps1`
   - Terminal 2: `.\start-node-only.ps1`

**Nodes auto-sync!** ✅

---

## 📚 Documentation

| Document | What's Inside |
|----------|---------------|
| **TWO-TERMINAL-SETUP.md** | Complete step-by-step guide |
| **QUICK-REFERENCE.md** | Commands and troubleshooting |
| **README-SCRIPTS.md** | How each script works |
| **ARCHITECTURE-DIAGRAM.md** | System diagrams and flow |
| **INDEX.md** | Documentation navigator |

---

## 🎓 How It Works

```
┌─────────────────────────┐
│     Terminal 1          │  
│  .\start-ngrok-tunnel   │
│         ↓               │
│   Creates public URL:   │
│  https://aaaa.ngrok.io  │
│   Forwards to:3010      │
└─────────────────────────┘
           ↑ ↓
    (HTTP Forwarding)
           ↑ ↓
┌─────────────────────────┐
│     Terminal 2          │
│  .\start-node-only      │
│         ↓               │
│  Node on :3010          │
│  P2P on :6001           │
│  Syncs Firebase         │
└─────────────────────────┘
```

---

## 💡 Why Two Terminals?

**Before:** Tried to run ngrok inside the node (complicated, hard to debug)

**Now:** Separate processes (clear, simple, controllable)

| Aspect | Two Terminals |
|--------|--------------|
| Control | Full |
| Debugging | Easy |
| Error handling | Clear |
| Sharing URLs | Simple |
| Multi-PC setup | Natural |

---

## 📋 Checklist

- [ ] Node.js installed (`node --version`)
- [ ] ngrok installed or available globally
- [ ] ngrok token in `.env`
- [ ] Dependencies installed (`npm install`)
- [ ] Terminal 1: `start-ngrok-tunnel.ps1` running
- [ ] Terminal 2: `start-node-only.ps1` running
- [ ] Can access http://localhost:3010/api/health
- [ ] Have ngrok public URL copied

---

## 🔧 Configuration

### .env File
```env
# Node Configuration
NODE_ID=node1                    # Your node name
PORT=3010                        # HTTP API port
P2P_PORT=6001                    # P2P network port

# ngrok Configuration
NGROK_AUTH_TOKEN=xxx             # From dashboard.ngrok.com
NGROK_REGION=in                  # Region (in=India, us=USA, etc.)

# Firebase Configuration
FIREBASE_DATABASE_URL=xxx        # For data persistence

# Bootstrap Nodes (for multi-PC)
BOOTSTRAP_NODES=https://xxx.ngrok.io,node1

# Security
JWT_SECRET=change-this           # Change in production
ADMIN_API_KEY=change-this        # Change in production

# Blockchain
ENABLE_DISTRIBUTED=true          # Enable P2P network
```

---

## 🚀 Startup Scripts

### `start-ngrok-tunnel.ps1`
```powershell
# What it does:
✓ Checks for ngrok
✓ Loads .env
✓ Authenticates with ngrok
✓ Creates tunnel to localhost:3010
✓ Displays public URL
✓ Keeps tunnel open
```

**Terminal:** Leave open
**Output:** Shows public URL

### `start-node-only.ps1`
```powershell
# What it does:
✓ Checks Node.js version
✓ Loads .env
✓ Installs dependencies if needed
✓ Initializes blockchain
✓ Starts P2P network
✓ Syncs with Firebase
✓ Listens on port 3010
```

**Terminal:** Leave open
**Output:** Shows server status

---

## 📱 Mobile App Integration

Once your node is running:

```javascript
// Use ngrok URL from Terminal 1
const BLOCKCHAIN_API = 'https://aaaa-bbbb-cccc.ngrok.io';

// Send transaction
fetch(`${BLOCKCHAIN_API}/mobile/api/transaction/send`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    from: 'farmer_id',
    to: 'buyer_id',
    amount: 1000,
    productName: 'Wheat',
    quantity: 50,
    unit: 'kg'
  })
});

// Get blockchain stats
fetch(`${BLOCKCHAIN_API}/mobile/api/blockchain/stats`)
  .then(r => r.json())
  .then(data => console.log(data));
```

---

## 🆘 Troubleshooting

### "ngrok not found"
```bash
npm install -g ngrok
# OR download from https://ngrok.com/download
```

### "NGROK_AUTH_TOKEN not set"
1. Go to https://dashboard.ngrok.com
2. Copy your Auth Token
3. Add to `.env`: `NGROK_AUTH_TOKEN=your_token`

### "Port 3010 already in use"
```powershell
netstat -ano | findstr :3010
taskkill /PID <PID> /F
```

### "Cannot connect to other nodes"
- Make sure PC 1's ngrok tunnel is still running (Terminal 1)
- Check ngrok URL is correct in PC 2's `.env`
- Wait 5 seconds for Firebase sync

---

## 📊 Useful Commands

```bash
# Check node health
curl http://localhost:3010/api/health

# See all nodes in network
curl http://localhost:3010/mobile/api/network/nodes

# Get blockchain stats
curl http://localhost:3010/mobile/api/blockchain/stats

# Send test transaction
curl -X POST http://localhost:3010/mobile/api/transaction/send \
  -H "Content-Type: application/json" \
  -d '{"from":"user1","to":"user2","amount":100}'

# View ngrok dashboard
# Open browser: http://localhost:4040
```

---

## 🔄 Data Flow

```
User App
    │
    ├─ HTTP Request
    │  (via ngrok URL)
    │
    ├─ ngrok tunnel
    │  (public ← → local)
    │
    ├─ Node HTTP API
    │  (:3010)
    │
    ├─ P2P Network
    │  (broadcasts to other nodes)
    │
    ├─ Firebase
    │  (persistent storage)
    │
    └─ Response
       (JSON)
```

---

## 📈 What's Included

**2 Startup Scripts:**
- `start-ngrok-tunnel.ps1` - ngrok only
- `start-node-only.ps1` - node only

**7 Documentation Files:**
- `TWO-TERMINAL-SETUP.md` - Complete guide
- `QUICK-REFERENCE.md` - Quick commands
- `README-SCRIPTS.md` - Script details
- `INDEX.md` - Documentation index
- `ARCHITECTURE-DIAGRAM.md` - System diagrams
- `SETUP-IMPROVEMENTS.md` - What's new
- `SETUP-COMPLETE.md` - Setup summary

**Core Application:**
- `app.js` - Entry point
- `server.js` - Express setup
- `blockchain.js` - Core logic
- `firebase.js` - Data persistence
- `.env` - Configuration

---

## ✅ You're Ready!

1. **Start Terminal 1:** `.\start-ngrok-tunnel.ps1`
2. **Start Terminal 2:** `.\start-node-only.ps1`
3. **Test:** `curl http://localhost:3010/api/health`
4. **Share URL:** Copy ngrok URL to other PCs
5. **Build:** Connect mobile app and start transacting!

---

## 📞 Need Help?

- **Quick start?** → Read `TWO-TERMINAL-SETUP.md`
- **Quick reference?** → Read `QUICK-REFERENCE.md`
- **Understanding?** → Read `ARCHITECTURE-DIAGRAM.md`
- **Lost?** → Read `INDEX.md`

---

## 🎉 Happy Blockchain Building!

Your distributed network awaits. Start with both scripts and get transacting!

```powershell
# Terminal 1
.\start-ngrok-tunnel.ps1

# Terminal 2 (new window)
.\start-node-only.ps1

# Done! 🎉
```

---

**Last Updated:** December 9, 2025
**Status:** ✅ Ready to Use
**Version:** 2.0 (Two-Terminal Setup)
