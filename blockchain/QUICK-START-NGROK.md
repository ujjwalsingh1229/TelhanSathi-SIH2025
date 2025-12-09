# ⚡ TelhanSathi Blockchain - Quick Start Guide

## 🎯 5-Minute Setup

### Prerequisites
```bash
# Check Node.js is installed
node -v    # Should be v14+
npm -v     # Should be v6+

# Check ngrok is installed
ngrok -v   # If not: npm install -g ngrok

# Get ngrok auth token from: https://dashboard.ngrok.com
```

### Step 1: Install Dependencies
```bash
cd c:\Users\Harsh\ Pandhe\Desktop\SIH\blockchain
npm install
```

### Step 2: Setup Firebase
1. Go to https://console.firebase.google.com/
2. Copy your **Database URL** (looks like: `https://xxx-rtdb.region.firebasedatabase.app`)

### Step 3: Configure .env
```bash
# Edit .env in blockchain folder
FIREBASE_DATABASE_URL=https://your-db.firebasedatabase.app
NGROK_AUTH_TOKEN=your_token_here
ENABLE_NGROK=true
ENABLE_DISTRIBUTED=true
```

### Step 4: Start Your Node
```bash
# PC 1
.\start-ngrok-node1.ps1

# PC 2 (different computer)
.\start-ngrok-node2.ps1

# PC 3 (different computer)
.\start-ngrok-node3.ps1
```

### Step 5: Test It
```bash
.\test-ngrok-system.ps1
```

---

## 📱 Mobile App Example

```javascript
// React Native / Flutter Code

const NODE_URL = 'https://xxxx-xxxx-xxxx.ngrok.io'; // From your node startup

// Send transaction
async function sendTransaction() {
  const response = await fetch(`${NODE_URL}/mobile/api/transaction/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: 'farmer_john',
      to: 'buyer_priya',
      amount: 5000,
      productName: 'Wheat',
      quantity: 100,
      unit: 'kg'
    })
  });
  return await response.json();
}

// Get blockchain stats
async function getStats() {
  const response = await fetch(`${NODE_URL}/mobile/api/blockchain/stats`);
  return await response.json();
}

// Get user transactions
async function getUserTxns(userId) {
  const response = await fetch(
    `${NODE_URL}/mobile/api/transactions?userId=${userId}&limit=20`
  );
  return await response.json();
}

// Get market feed
async function getMarketFeed() {
  const response = await fetch(`${NODE_URL}/mobile/api/market/feed?limit=50`);
  return await response.json();
}
```

---

## 🔗 Network Architecture

```
PC 1 (Node 1)          PC 2 (Node 2)          PC 3 (Node 3)
      │                     │                      │
      ├─ ngrok: https://aaa ├─ ngrok: https://bbb ├─ ngrok: https://ccc
      │                     │                      │
      └─────────────────────┼──────────────────────┘
                             │
                     Firebase Realtime DB
                     (nodes, blockchain)
                             │
                ┌────────────┴────────────┐
                │                         │
           Mobile Apps          Browser Dashboard
           (Farmers, Buyers)     (Admin Panel)
```

---

## ✅ Working Features

- ✅ **Multi-PC Deployment** - Run different nodes on different computers
- ✅ **Public URLs** - ngrok exposes each node publicly (no port forwarding)
- ✅ **Auto Node Discovery** - Nodes find each other via Firebase automatically
- ✅ **Persistent Storage** - Blockchain data stored in Firebase Realtime DB
- ✅ **Mobile API** - Full REST API for mobile apps
- ✅ **Real-time Sync** - Transactions sync across all nodes
- ✅ **Market Feed** - View all recent transactions in network
- ✅ **User Stats** - Track individual user transaction history

---

## 📡 Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/mobile/api/health` | GET | Check node status |
| `/mobile/api/transaction/send` | POST | Send transaction |
| `/mobile/api/transactions?userId=X` | GET | Get user's transactions |
| `/mobile/api/blockchain/stats` | GET | Get blockchain stats |
| `/mobile/api/blockchain/latest?count=10` | GET | Get latest blocks |
| `/mobile/api/network/nodes` | GET | List all active nodes |
| `/mobile/api/network/validators` | GET | List validators |
| `/mobile/api/market/feed?limit=50` | GET | Get market activity |
| `/mobile/api/user/{userId}/stats` | GET | Get user statistics |

---

## 🚀 Deploy to Multiple PCs

### PC 1: Validator Node
```powershell
# .env
NODE_ID=node1
PORT=3010
P2P_PORT=6001
IS_VALIDATOR=true
ENABLE_NGROK=true
ENABLE_DISTRIBUTED=true

.\start-ngrok-node1.ps1
# Output: https://aaaa-bbbb-cccc.ngrok.io
```

### PC 2: Observer Node
```powershell
# .env
NODE_ID=node2
PORT=3010  # Different computer can use same port
P2P_PORT=6001  # Different computer can use same port
IS_VALIDATOR=false
ENABLE_NGROK=true
ENABLE_DISTRIBUTED=true
BOOTSTRAP_NODES=https://aaaa-bbbb-cccc.ngrok.io,node1

.\start-ngrok-node2.ps1
# Output: https://xxxx-yyyy-zzzz.ngrok.io
```

### PC 3: Observer Node
```powershell
# .env
NODE_ID=node3
PORT=3010
P2P_PORT=6001
IS_VALIDATOR=false
ENABLE_NGROK=true
ENABLE_DISTRIBUTED=true
BOOTSTRAP_NODES=https://aaaa-bbbb-cccc.ngrok.io,node1

.\start-ngrok-node3.ps1
# Output: https://wwww-pppp-mmmm.ngrok.io
```

---

## 📊 Firebase Structure

Blockchain data is stored at:
```
Firebase Root
├── nodes/
│   └── registry/
│       ├── node1: { nodeId, publicUrl, isValidator, reputation, timestamp }
│       ├── node2: { ... }
│       └── node3: { ... }
├── blockchain/
│   ├── blocks: [ { index, hash, timestamp, data, ... }, ... ]
│   └── transactions: [ { ... } ]
└── transactions/
    └── pool: [ pending transactions ]
```

---

## 🐛 Common Issues

**Q: ngrok not found?**
```bash
npm install -g ngrok
```

**Q: Firebase connection error?**
- Check database URL in .env
- Verify Firebase Realtime DB is created
- Check database rules (Test Mode is OK)

**Q: Nodes not connecting?**
- Verify all nodes can reach ngrok
- Check BOOTSTRAP_NODES URL
- Look at node console output for errors

**Q: Blockchain not syncing?**
- Check Firebase is working: `curl https://your-db.firebasedatabase.app.json`
- Restart nodes
- Check network connectivity

---

## 📞 Next Steps

1. **Test Basic Operation**: `.\test-ngrok-system.ps1`
2. **Create Mobile App**: Use endpoints in your app
3. **Monitor Dashboard**: Check Firebase Console
4. **Scale Up**: Add more nodes as needed
5. **Production Deploy**: Harden security, add auth

---

## 🔐 Security Notes

- Current setup: **Test Mode** (OK for development)
- For production:
  - Enable Firebase authentication
  - Add JWT token validation
  - Use HTTPS certificates
  - Implement rate limiting
  - Add input validation

---

## 💡 Tips

1. **One PC = Multiple Nodes**: Can run multiple nodes on same PC (different ports)
2. **Offline = Local Network**: If ngrok unavailable, use local IPs (192.168.x.x)
3. **Firebase = Global**: All nodes see same blockchain (consistency guaranteed)
4. **Mobile First**: All APIs designed for mobile app usage
5. **Auto-Discovery**: Nodes register in Firebase automatically

---

**Questions?** Check `NGROK-DEPLOYMENT-GUIDE.md` for detailed documentation.
