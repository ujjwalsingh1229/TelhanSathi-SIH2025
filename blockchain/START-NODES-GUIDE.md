# 🚀 How to Start Nodes - Simple Step-by-Step Guide

## ⭐ RECOMMENDED: Two-Terminal Setup

**See `TWO-TERMINAL-SETUP.md` for the recommended approach:**
- **Terminal 1:** ngrok tunnel (you see the public URL)
- **Terminal 2:** blockchain node
- Easy to manage and debug
- Perfect for multi-PC setup

Quick reference:
```bash
# Terminal 1
.\start-ngrok-tunnel.ps1

# Terminal 2
.\start-node-only.ps1
```

---

## Alternative: Starting on THIS PC (Local Testing - No ngrok)

### Option 1: Start Single Node (Easiest - 2 minutes)

**Step 1: Open PowerShell**
```bash
# Press Windows + R, type "powershell", press Enter
```

**Step 2: Go to blockchain folder**
```bash
cd "c:\Users\Harsh Pandhe\Desktop\SIH\blockchain"
```

**Step 3: Start the node**
```bash
node app.js
```

**You should see:**
```
🚀 Initializing TelhanSathi Blockchain...
   Node ID: node1
   HTTP Port: 3000
   P2P Port: 6001
   Distributed Mode: DISABLED

✅ Blockchain initialized successfully
📡 Server running on: http://localhost:3000
```

**✅ Done! Your node is running!**

### Option 2: Start Multiple Nodes Locally (10 minutes)

**Open 3 separate PowerShell windows:**

**Window 1 - Node 1:**
```bash
cd "c:\Users\Harsh Pandhe\Desktop\SIH\blockchain"
node app.js
# Runs on http://localhost:3000
```

**Window 2 - Node 2:**
```bash
cd "c:\Users\Harsh Pandhe\Desktop\SIH\blockchain"
$env:NODE_ID = "node2"
$env:PORT = "3001"
$env:P2P_PORT = "6002"
$env:BOOTSTRAP_NODES = "ws://localhost:6001,node1"
node app.js
# Runs on http://localhost:3001
```

**Window 3 - Node 3:**
```bash
cd "c:\Users\Harsh Pandhe\Desktop\SIH\blockchain"
$env:NODE_ID = "node3"
$env:PORT = "3002"
$env:P2P_PORT = "6003"
$env:BOOTSTRAP_NODES = "ws://localhost:6001,node1"
node app.js
# Runs on http://localhost:3002
```

**✅ All 3 nodes are now running locally and syncing!**

---

## Starting with ngrok (Multi-PC - Public URLs)

### Prerequisites
```bash
# 1. Get ngrok account: https://dashboard.ngrok.com
# 2. Copy your auth token from dashboard
# 3. Install ngrok globally
npm install -g ngrok
```

### Step-by-Step: This PC with ngrok

**Step 1: Create .env file**

Go to `c:\Users\Harsh Pandhe\Desktop\SIH\blockchain` folder and create `.env` file with:

```env
NGROK_AUTH_TOKEN=2FJsXEfAwU9gt5pjCvure8ftLmN_3KoCk1HQfshvSLbd8of6X
ENABLE_NGROK=true
ENABLE_DISTRIBUTED=true
```

**Step 2: Edit startup script**

Open `start-ngrok-node1.ps1` and make sure it has:
```powershell
$env:ENABLE_NGROK = "true"
$env:NODE_ID = "node1"
$env:PORT = "3010"
node app.js
```

**Step 3: Run it**
```bash
cd "c:\Users\Harsh Pandhe\Desktop\SIH\blockchain"
.\start-ngrok-node1.ps1
```

**You should see:**
```
🚀 Starting Node 1 (Validator)
   HTTP Port: 3010
   P2P Port: 6001

🌐 ngrok tunnel created: https://xxxx-xxxx-xxxx.ngrok.io
   Node ID: node1
   Local: http://localhost:3010
   Public: https://xxxx-xxxx-xxxx.ngrok.io

✅ Node registered in Firebase network
```

**✅ Your node has a public URL!**

---

## Starting on DIFFERENT PCs (Multi-PC Setup)

### PC 1 (This Computer) - Validator Node

**Steps:**
1. Create `.env` file with ngrok token
2. Run: `.\start-ngrok-node1.ps1`
3. **Copy the ngrok URL** (you'll need it for PC 2 & PC 3)

**Example Output:**
```
Public: https://aaaa-bbbb-cccc.ngrok.io
```

### PC 2 (Another Computer) - Observer Node

**Step 1: Copy project folder**
- Copy entire `blockchain` folder to PC 2
- Or clone from git if available

**Step 2: Install dependencies**
```bash
cd blockchain
npm install
```

**Step 3: Create .env file**
```env
NGROK_AUTH_TOKEN=your_token_here
ENABLE_NGROK=true
ENABLE_DISTRIBUTED=true
BOOTSTRAP_NODES=https://aaaa-bbbb-cccc.ngrok.io,node1
```
⚠️ **Replace `aaaa-bbbb-cccc.ngrok.io` with URL from PC 1!**

**Step 4: Edit start-ngrok-node2.ps1**
```powershell
# Make sure it has:
$env:ENABLE_NGROK = "true"
$env:NODE_ID = "node2"
$env:PORT = "3010"  # Same port is OK on different PC
$env:BOOTSTRAP_NODES = "https://aaaa-bbbb-cccc.ngrok.io,node1"
```

**Step 5: Run it**
```bash
.\start-ngrok-node2.ps1
```

**You should see:**
```
✅ Connecting to bootstrap node: https://aaaa-bbbb-cccc.ngrok.io
✅ Node registered in Firebase network
🌐 ngrok tunnel created: https://xxxx-yyyy-zzzz.ngrok.io
```

### PC 3 (Another Computer) - Observer Node

**Repeat same as PC 2:**
1. Copy project folder
2. `npm install`
3. Create `.env` with same ngrok token
4. Update `BOOTSTRAP_NODES=https://aaaa-bbbb-cccc.ngrok.io,node1`
5. Run `.\start-ngrok-node3.ps1`

---

## ✅ Verify All Nodes Are Connected

### Test 1: Check each node's health

**On PC 1:**
```bash
curl http://localhost:3010/mobile/api/health | jq
```

**On PC 2:**
```bash
curl http://localhost:3010/mobile/api/health | jq
```

**On PC 3:**
```bash
curl http://localhost:3010/mobile/api/health | jq
```

### Test 2: See all connected nodes

```bash
# Run on ANY node
curl http://localhost:3010/mobile/api/network/nodes | jq
```

**You should see 3 nodes:**
```json
{
  "nodeCount": 3,
  "nodes": [
    {
      "nodeId": "node1",
      "publicUrl": "https://aaaa-bbbb-cccc.ngrok.io",
      "isValidator": true
    },
    {
      "nodeId": "node2",
      "publicUrl": "https://xxxx-yyyy-zzzz.ngrok.io",
      "isValidator": false
    },
    {
      "nodeId": "node3",
      "publicUrl": "https://wwww-pppp-mmmm.ngrok.io",
      "isValidator": false
    }
  ]
}
```

### Test 3: Send a test transaction

```bash
# From PC 1
curl -X POST http://localhost:3010/mobile/api/transaction/send \
  -H "Content-Type: application/json" \
  -d '{
    "from": "farmer1",
    "to": "buyer1",
    "amount": 100,
    "productName": "Wheat"
  }'
```

### Test 4: Verify it's on all nodes

**On PC 1:**
```bash
curl http://localhost:3010/mobile/api/blockchain/stats | jq
```

**On PC 2:**
```bash
curl http://localhost:3010/mobile/api/blockchain/stats | jq
```

**On PC 3:**
```bash
curl http://localhost:3010/mobile/api/blockchain/stats | jq
```

**All should show same block count and transactions** ✅

---

## 🔄 How Nodes Sync (Behind the Scenes)

### Automatic Sync Process:

```
PC 1 (Node 1)              PC 2 (Node 2)              PC 3 (Node 3)
   │                          │                          │
   │ ─────ngrok─────────────────> (Connect via ngrok)
   │                          │
   │ <──────P2P (WebSocket)───────
   │ ───────P2P (WebSocket)────────>
   │                          │
   └──────────────────────────┼──────────────────────────┘
                              │
                     Firebase Realtime DB
                     (all data synced here)
```

### What Gets Synced:

1. **New Transactions** - Broadcast to all nodes in <1 second
2. **New Blocks** - Created on validator, sent to all nodes
3. **Node List** - Registered in Firebase (heartbeat every 30s)
4. **Blockchain Data** - Saved to Firebase for persistence

### Why Sync Happens:

- **WebSocket P2P**: Real-time peer-to-peer messaging
- **Firebase**: Persistent storage + fallback sync
- **Automatic**: No manual intervention needed

---

## 📱 Connect Mobile App to the Network

### Get Public URLs

**Run this on each PC:**
```bash
# Shows the ngrok public URL
curl http://localhost:3010/mobile/api/health | jq '.node.publicUrl'
```

### In Your Mobile App

```javascript
// PC 1 URL
const PC1 = 'https://aaaa-bbbb-cccc.ngrok.io';
const PC2 = 'https://xxxx-yyyy-zzzz.ngrok.io';
const PC3 = 'https://wwww-pppp-mmmm.ngrok.io';

// Try to connect to any available node
async function connectToBlockchain() {
  const nodes = [PC1, PC2, PC3];
  
  for (const nodeUrl of nodes) {
    try {
      const response = await fetch(`${nodeUrl}/mobile/api/health`);
      if (response.ok) {
        return nodeUrl;  // Connected!
      }
    } catch (error) {
      continue;  // Try next node
    }
  }
}

// Send transaction
const nodeUrl = await connectToBlockchain();
fetch(`${nodeUrl}/mobile/api/transaction/send`, {
  method: 'POST',
  body: JSON.stringify({
    from: 'farmer1',
    to: 'buyer1',
    amount: 100
  })
});
```

---

## ⚡ Quick Reference

### Local Testing (Same PC)
```
PC 1:
  node app.js
  → http://localhost:3000

PC 2 (same machine):
  $env:PORT=3001; node app.js
  → http://localhost:3001
```

### Multi-PC Testing (Different Computers)

**PC 1:**
```
.\start-ngrok-node1.ps1
→ https://aaaa.ngrok.io
```

**PC 2:**
```
Set BOOTSTRAP_NODES=https://aaaa.ngrok.io,node1
.\start-ngrok-node2.ps1
→ https://xxxx.ngrok.io
```

**PC 3:**
```
Set BOOTSTRAP_NODES=https://aaaa.ngrok.io,node1
.\start-ngrok-node3.ps1
→ https://wwww.ngrok.io
```

---

## 🆘 Troubleshooting

### Node won't start

**Problem:** "Cannot find module"
```bash
# Solution: Install dependencies
npm install
```

**Problem:** "Port already in use"
```bash
# Solution: Use different port
$env:PORT=3050
node app.js
```

### Nodes not connecting

**Problem:** "Cannot connect to bootstrap node"
```
# Check:
1. Is PC 1 ngrok URL correct?
2. Is BOOTSTRAP_NODES in .env correct?
3. Is PC 1 still running?
```

**Problem:** "Firebase connection error"
```
# Check:
1. Do you have FIREBASE_DATABASE_URL in .env?
2. Is Firebase Realtime Database created?
```

### Transactions not syncing

**Problem:** "Transaction on PC 1 not showing on PC 2"
```bash
# Check sync status
curl http://localhost:3010/mobile/api/blockchain/stats | jq
curl http://localhost:3011/mobile/api/blockchain/stats | jq
# Should have same block count
```

---

## ✅ Checklist: Multi-PC Setup

- [ ] PC 1: Created `.env` with NGROK_AUTH_TOKEN
- [ ] PC 1: Running `.\start-ngrok-node1.ps1` ✓
- [ ] PC 1: Got ngrok public URL (https://aaaa...)
- [ ] PC 2: Copied `blockchain` folder
- [ ] PC 2: Ran `npm install`
- [ ] PC 2: Created `.env` with ngrok token
- [ ] PC 2: Added `BOOTSTRAP_NODES=https://aaaa...,node1` to `.env`
- [ ] PC 2: Running `.\start-ngrok-node2.ps1` ✓
- [ ] PC 3: Repeated PC 2 steps
- [ ] All 3 nodes show in `/mobile/api/network/nodes` ✓
- [ ] Sent test transaction from PC 1
- [ ] Transaction visible on PC 2 & PC 3 ✓

---

## 📊 Node Status Commands

**Check if node is running:**
```bash
curl http://localhost:3010/mobile/api/health
```

**See all nodes in network:**
```bash
curl http://localhost:3010/mobile/api/network/nodes | jq
```

**Get blockchain stats:**
```bash
curl http://localhost:3010/mobile/api/blockchain/stats | jq
```

**Send test transaction:**
```bash
curl -X POST http://localhost:3010/mobile/api/transaction/send \
  -H "Content-Type: application/json" \
  -d '{"from":"user1","to":"user2","amount":100}'
```

---

## 🎯 Summary

| Task | Time | Command |
|------|------|---------|
| Start 1 node locally | 30s | `node app.js` |
| Start 3 nodes locally | 2min | 3x PowerShell + env vars |
| Start 1 node with ngrok | 1min | `.\start-ngrok-node1.ps1` |
| Connect PC 2 to PC 1 | 5min | Update .env + run script |
| Verify all synced | 30s | Check `/network/nodes` |
| Send test transaction | 10s | cURL command |

**Total setup time: 10-15 minutes for full multi-PC network!**

---

## 📖 Next: See Detailed Guides

- **Local testing:** See `QUICK-START-NGROK.md`
- **Production setup:** See `NGROK-DEPLOYMENT-GUIDE.md`
- **Mobile integration:** See `API-TESTING-EXAMPLES.md`

---

**Ready to start? Pick your option and run the command!** 🚀
