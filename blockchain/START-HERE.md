# 🚀 Quick Start Guide - TelhanSathi Distributed Blockchain

## ✅ System Ready!

Your blockchain is now a **production-ready distributed system** with:
- ✅ Peer-to-Peer Network
- ✅ Proof of Authority Consensus
- ✅ Admin-Controlled Validators
- ✅ Automatic Chain Synchronization
- ✅ Triple-Redundant Storage

---

## 🎯 Choose Your Mode

### Mode 1: Single Node (Simple Testing)

```bash
npm start
```

**Access:** http://localhost:3000  
**Use Case:** Development, testing basic transactions

---

### Mode 2: Distributed Network (Production Mode)

#### Step 1: Start First Node (Validator)

```bash
npm run node1
```

**Node 1 Details:**
- HTTP API: http://localhost:3000
- P2P Network: ws://localhost:6001
- Role: Validator (can create blocks)

#### Step 2: Start Second Node (Peer)

Open a **new terminal** and run:

```bash
npm run node2
```

**Node 2 Details:**
- HTTP API: http://localhost:3001
- P2P Network: ws://localhost:6002
- Role: Peer (validates blocks)
- Auto-connects to Node 1

#### Step 3: Start Third Node (Validator)

Open **another terminal** and run:

```bash
npm run node3
```

**Node 3 Details:**
- HTTP API: http://localhost:3002
- P2P Network: ws://localhost:6003
- Role: Validator
- Auto-connects to Node 1

---

## 🧪 Test Your Blockchain

### 1️⃣ Add a Transaction (Any Node)

```bash
curl -X POST http://localhost:3000/transaction/add -H "Content-Type: application/json" -d "{\"from\":\"farmer1\",\"to\":\"buyer1\",\"amount\":5000,\"crop\":\"Wheat\",\"quantity\":\"100 kg\"}"
```

**Expected:** Transaction added, block mined, broadcast to all nodes

### 2️⃣ Check Blockchain on Different Nodes

```bash
# Check Node 1
curl http://localhost:3000/blockchain

# Check Node 2
curl http://localhost:3001/blockchain

# Check Node 3
curl http://localhost:3002/blockchain
```

**Expected:** All nodes show the **same blockchain** (synchronized!)

### 3️⃣ View Network Status

```bash
curl http://localhost:3000/admin/network/status -H "x-admin-key: admin-key-change-this-in-production-SIH2025"
```

**Expected:** See all connected peers, validators, and network health

---

## 🔑 Admin Commands

### Promote Node to Validator

```bash
curl -X POST http://localhost:3000/admin/nodes/promote/node2 -H "x-admin-key: admin-key-change-this-in-production-SIH2025"
```

### View All Nodes

```bash
curl http://localhost:3000/admin/nodes -H "x-admin-key: admin-key-change-this-in-production-SIH2025"
```

### Force Chain Sync

```bash
curl -X POST http://localhost:3000/admin/network/sync -H "x-admin-key: admin-key-change-this-in-production-SIH2025"
```

---

## 📊 Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/transaction/add` | POST | Add new transaction |
| `/blockchain` | GET | View entire blockchain |
| `/transaction/:id` | GET | Get specific transaction |
| `/stats` | GET | Blockchain statistics |
| `/admin/network/status` | GET | Network health |
| `/admin/nodes` | GET | List all nodes |

---

## 🔐 Security Notes

### Production Deployment:

1. **Change Admin Key**
   - Edit `.env` → `ADMIN_API_KEY=<your-secret-key>`

2. **Change JWT Secret**
   - Edit `.env` → `JWT_SECRET=<your-jwt-secret>`

3. **Enable Distributed Mode**
   - Edit `.env` → `ENABLE_DISTRIBUTED=true`

4. **Add Real Node URLs**
   - Edit `.env` → `BOOTSTRAP_NODES=ws://node1.example.com:6001|node1`

---

## 📁 Data Storage Locations

### Single Node:
- Firebase Cloud

### Distributed Network:
- **Node 1:** `blockchain-data/blockchain.json`
- **Node 2:** `blockchain-data/blockchain.json`
- **Node 3:** `blockchain-data/blockchain.json`
- **Cloud:** Firebase (shared backup)

---

## ❓ Troubleshooting

### Nodes Not Connecting?
- Check firewall allows WebSocket connections
- Verify `P2P_PORT` is not already in use
- Check `BOOTSTRAP_NODES` URLs are correct

### Blockchain Not Syncing?
- Run: `curl -X POST http://localhost:3000/admin/network/sync -H "x-admin-key: <key>"`
- Check all nodes are running
- Verify validators are active

### Transaction Not Broadcasting?
- Ensure `ENABLE_DISTRIBUTED=true` in `.env`
- Check node has active peer connections
- Verify node is approved (check `/admin/nodes`)

---

## 📚 Full Documentation

For complete API reference and advanced features, see:
- **DISTRIBUTED-GUIDE.md** - Full distributed system documentation
- **README.md** - Original blockchain documentation

---

## 🎉 You're Ready!

Your blockchain is now a **true distributed ledger** ready to secure your marketplace transactions!

**Next Steps:**
1. Test with 3 nodes running simultaneously
2. Add transactions and watch them sync
3. Integrate with your marketplace app
4. Deploy to production servers

**Questions?** Check `DISTRIBUTED-GUIDE.md` for detailed information.
