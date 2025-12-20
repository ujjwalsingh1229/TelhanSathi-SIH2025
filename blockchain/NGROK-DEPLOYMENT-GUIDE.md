# 🌐 TelhanSathi Blockchain - Multi-PC ngrok Deployment Guide

## Overview
This guide explains how to deploy the TelhanSathi blockchain system across multiple PCs using **ngrok** for public tunneling and **Firebase Realtime Database** for node discovery and blockchain persistence.

**Key Features:**
- 🌍 Run blockchain nodes on different computers
- 🔗 Public URLs via ngrok (no port forwarding needed)
- 📱 Mobile app can connect to any node
- 🔄 Automatic node discovery via Firebase
- 💾 Persistent blockchain storage in Firebase
- ✅ Distributed consensus (Proof of Authority)

---

## Prerequisites

### 1. Install Required Software

**Node.js & npm** (v14+):
```bash
# Download from https://nodejs.org/
# Or use package manager:
# Windows: choco install nodejs
# Mac: brew install node
# Linux: sudo apt install nodejs npm
```

**ngrok** (for public tunneling):
```bash
# Option 1: npm
npm install -g ngrok

# Option 2: Download directly
# https://ngrok.com/download
```

**Git** (for version control):
```bash
# https://git-scm.com/
```

### 2. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create Project"
3. Name: `telhan-sathi-blockchain`
4. Enable Google Analytics (optional)
5. Create project
6. In left sidebar → "Realtime Database"
7. Click "Create Database"
8. Choose location (India: `asia-southeast1`)
9. Start in **Test mode**
10. Copy your database URL from the settings

### 3. Get ngrok Auth Token

1. Go to [ngrok Dashboard](https://dashboard.ngrok.com/)
2. Sign up / Sign in
3. Copy your "Auth Token"
4. You'll need this for production deployment

---

## Setup Instructions

### Step 1: Clone/Setup Project

```bash
cd your-blockchain-folder
git clone <repo-url>  # or download ZIP
cd SIH/blockchain
npm install
```

### Step 2: Configure Environment Variables

Create `.env` file in the `blockchain/` directory:

```env
# Firebase (from your Firebase project settings)
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your_domain.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_DATABASE_URL=https://your-db-name.firebasedatabase.app

# ngrok Configuration
ENABLE_NGROK=true
NGROK_AUTH_TOKEN=your_ngrok_token_here
NGROK_REGION=in  # Change based on your region (us, eu, in, etc.)

# Node Configuration (per PC)
NODE_ID=node1        # Change per machine: node1, node2, node3, etc.
PORT=3010           # Change per machine: 3010, 3011, 3012, etc.
P2P_PORT=6001       # Change per machine: 6001, 6002, 6003, etc.
IS_VALIDATOR=true   # true for validator nodes, false for observer nodes

# Distributed Mode
ENABLE_DISTRIBUTED=true

# Bootstrap Nodes (optional - after first node is running)
# BOOTSTRAP_NODES=https://xxxx-xxxx-xxxx.ngrok.io,node1

# JWT & Security
JWT_SECRET=your-super-secret-key-change-this
JWT_EXPIRY=24h

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

### Step 3: Start Single Node (Test)

```bash
# On PC 1
.\start-ngrok-node1.ps1

# Wait for output like:
# 🌐 ngrok tunnel created: https://xxxx-xxxx-xxxx.ngrok.io
# ✅ Node registered in Firebase network
```

### Step 4: Start Additional Nodes

**On PC 2:**
```bash
# Edit .env: NODE_ID=node2, PORT=3011, P2P_PORT=6002
.\start-ngrok-node2.ps1
```

**On PC 3:**
```bash
# Edit .env: NODE_ID=node3, PORT=3012, P2P_PORT=6003
.\start-ngrok-node3.ps1
```

---

## API Endpoints

### Mobile App Endpoints

All endpoints are accessible via ngrok public URL or localhost:

#### Health Check
```
GET /mobile/api/health
Response: { status: "healthy", blockchain: {...}, node: {...} }
```

#### Send Transaction
```
POST /mobile/api/transaction/send
Body: {
  "from": "farmer_id",
  "to": "buyer_id",
  "amount": 1000,
  "productName": "Wheat",
  "quantity": 50,
  "unit": "kg"
}
Response: { success: true, transaction: {...} }
```

#### Get User Transactions
```
GET /mobile/api/transactions?userId=farmer_123&limit=20
Response: { transactions: [...] }
```

#### Blockchain Stats
```
GET /mobile/api/blockchain/stats
Response: { statistics: { totalBlocks, totalTransactions, chainValid, ... } }
```

#### Get Latest Blocks
```
GET /mobile/api/blockchain/latest?count=10
Response: { blocks: [...] }
```

#### Get Active Nodes
```
GET /mobile/api/network/nodes
Response: { nodeCount: 3, nodes: [...] }
```

#### Get Validators
```
GET /mobile/api/network/validators
Response: { validatorCount: 1, validators: [...] }
```

#### Market Feed
```
GET /mobile/api/market/feed?limit=50
Response: { feed: [recent transactions...] }
```

#### User Stats
```
GET /mobile/api/user/{userId}/stats
Response: { statistics: { transactionsSent, transactionsReceived, ... } }
```

---

## Using ngrok URLs

Once a node starts with ngrok, you'll see output like:
```
🌐 ngrok tunnel created: https://xxxx-1234-xxxx.ngrok.io
   Node ID: node1
   Local: http://localhost:3010
   Public: https://xxxx-1234-xxxx.ngrok.io
```

### For Mobile App:
```
POST https://xxxx-1234-xxxx.ngrok.io/mobile/api/transaction/send
GET https://xxxx-1234-xxxx.ngrok.io/mobile/api/blockchain/stats
```

### Node Discovery:
All nodes automatically register in Firebase and discover each other via:
- `GET /mobile/api/network/nodes` - List all active nodes
- Firebase stores node URLs → mobile app can connect to any available node

---

## Example: Mobile App Integration

```javascript
// Example: React Native or Flutter

const API_BASE = 'https://xxxx-1234-xxxx.ngrok.io';

// Send transaction
async function sendTransaction(from, to, amount, product) {
  const response = await fetch(`${API_BASE}/mobile/api/transaction/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ from, to, amount, productName: product, quantity: 1 })
  });
  return response.json();
}

// Get blockchain stats
async function getStats() {
  const response = await fetch(`${API_BASE}/mobile/api/blockchain/stats`);
  return response.json();
}

// Get user transactions
async function getUserTransactions(userId) {
  const response = await fetch(
    `${API_BASE}/mobile/api/transactions?userId=${userId}&limit=20`
  );
  return response.json();
}

// Discover nodes
async function discoverNodes() {
  const response = await fetch(`${API_BASE}/mobile/api/network/nodes`);
  return response.json();
}
```

---

## Connecting Nodes Across Different PCs

### Option 1: Using Bootstrap Nodes (Recommended)

After Node 1 starts and gets its ngrok URL, update Node 2 & 3:

```env
# Node 2 .env
BOOTSTRAP_NODES=https://xxxx-1234-xxxx.ngrok.io,node1

# Node 3 .env
BOOTSTRAP_NODES=https://xxxx-1234-xxxx.ngrok.io,node1
```

Then start the nodes. They'll automatically discover each other via:
1. P2P WebSocket connections to bootstrap node
2. Firebase node discovery (automatic registration)

### Option 2: Firebase Auto-Discovery

All nodes register in Firebase automatically:
- Any node can query `/mobile/api/network/nodes` to see all other nodes
- Nodes automatically sync blockchain data via Firebase

---

## Troubleshooting

### ngrok Issues
```bash
# ngrok not found?
npm install -g ngrok

# Check ngrok status
ngrok -v

# Auth token invalid?
# 1. Get new token from https://dashboard.ngrok.com
# 2. Update NGROK_AUTH_TOKEN in .env
# 3. Restart node
```

### Firebase Connection Issues
```bash
# Check database URL
# Format: https://PROJECT-ID-rtdb.REGION.firebasedatabase.app

# Verify in .env file is correct

# Test with curl:
curl https://your-db.firebasedatabase.app/nodes.json
```

### Node Discovery Not Working
```bash
# Check if Firebase Realtime Database is accessible
# 1. Go to Firebase Console
# 2. Verify database is "Test Mode" or has proper rules
# 3. Check Rules:
{
  "rules": {
    "nodes": {
      ".read": true,
      ".write": true
    },
    "blockchain": {
      ".read": true,
      ".write": true
    }
  }
}
```

### Multiple PCs on Same Network

If on same WiFi, you can also use local IPs:
```env
# Instead of ngrok URL, use:
BOOTSTRAP_NODES=ws://192.168.x.x:6001,node1
```

---

## Monitoring & Testing

### Test Node Health
```bash
# Check if node is running
curl http://localhost:3010/mobile/api/health

# Via ngrok public URL
curl https://xxxx-xxxx-xxxx.ngrok.io/mobile/api/health
```

### Monitor Firebase
1. Go to Firebase Console
2. Realtime Database → Data
3. Watch `nodes/registry` for active node updates
4. Watch `blockchain` for new blocks

### Test Transaction Flow
```bash
# 1. Send transaction
curl -X POST https://xxxx-xxxx-xxxx.ngrok.io/mobile/api/transaction/send \
  -H "Content-Type: application/json" \
  -d '{
    "from": "farmer1",
    "to": "buyer1",
    "amount": 1000,
    "productName": "Wheat"
  }'

# 2. Check blockchain stats
curl https://xxxx-xxxx-xxxx.ngrok.io/mobile/api/blockchain/stats

# 3. Get user transactions
curl https://xxxx-xxxx-xxxx.ngrok.io/mobile/api/transactions?userId=farmer1
```

---

## Production Checklist

- [ ] All `.env` files configured correctly
- [ ] ngrok auth tokens set up
- [ ] Firebase database rules are correct (Test Mode OK for now)
- [ ] All nodes can reach Firebase
- [ ] ngrok tunnels are stable (restart if needed)
- [ ] Mobile app can connect to ngrok URLs
- [ ] Transactions broadcast correctly between nodes
- [ ] Blockchain stays in sync across nodes
- [ ] Node reputation system working
- [ ] All 3+ nodes show in `/mobile/api/network/nodes`

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Internet (ngrok tunnels)                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│   PC 1                    PC 2                    PC 3        │
│  ┌─────────┐          ┌─────────┐          ┌─────────┐      │
│  │ Node 1  │◄────────►│ Node 2  │◄────────►│ Node 3  │      │
│  │(Validator)         │(Observer)         │(Observer)      │
│  └────┬────┘          └────┬────┘          └────┬────┘      │
│       │                    │                    │            │
│       └────────────────────┼────────────────────┘            │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │     Firebase    │                        │
│                   │  Realtime DB    │                        │
│                   │  - nodes/       │                        │
│                   │  - blockchain/  │                        │
│                   └─────────────────┘                        │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                     Mobile Apps                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Farmer App  │  │  Buyer App   │  │  Vendor App  │      │
│  │              │  │              │  │              │      │
│  │ POST /tx     │  │ GET /stats   │  │ GET /feed    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Support & Documentation

- 📖 [Firebase Documentation](https://firebase.google.com/docs)
- 🔗 [ngrok Documentation](https://ngrok.com/docs)
- 🚀 [Node.js Documentation](https://nodejs.org/docs/)
- 📱 [WebSocket API Reference](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

**For issues or questions:**
- Check logs in terminal windows
- Verify .env configuration
- Test ngrok connectivity: `ngrok -v`
- Check Firebase console for data updates
