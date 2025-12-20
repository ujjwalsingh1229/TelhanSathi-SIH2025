# 📖 API Reference - TelhanSathi Blockchain

Complete API documentation for your distributed blockchain system.

---

## 🔓 Public Endpoints

### 1. Add Transaction

**Endpoint:** `POST /transaction/add`

**Description:** Add a new transaction to the blockchain (will be broadcast to all nodes if distributed mode is enabled).

**Request Body:**
```json
{
  "from": "farmer123",
  "to": "buyer456",
  "amount": 10000,
  "crop": "Wheat",
  "quantity": "500 kg",
  "upiTransactionId": "UPI123456789",
  "location": "Mandi ABC"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Transaction added successfully",
  "blockHash": "0000a1b2c3d4e5f6...",
  "blockIndex": 42,
  "transactionId": "txn_123456",
  "distributed": true,
  "broadcasted": true
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:3000/transaction/add \
  -H "Content-Type: application/json" \
  -d '{
    "from": "farmer1",
    "to": "buyer1",
    "amount": 5000,
    "crop": "Wheat",
    "quantity": "100 kg"
  }'
```

---

### 2. Get Entire Blockchain

**Endpoint:** `GET /blockchain`

**Description:** Retrieve the complete blockchain.

**Response:**
```json
{
  "success": true,
  "blockchain": [
    {
      "index": 0,
      "timestamp": "2025-01-20T10:00:00.000Z",
      "transactions": [],
      "previousHash": "0",
      "hash": "genesis-block-hash",
      "nonce": 0
    },
    {
      "index": 1,
      "timestamp": "2025-01-20T10:05:00.000Z",
      "transactions": [...],
      "previousHash": "genesis-block-hash",
      "hash": "0000abc123...",
      "nonce": 12345,
      "merkleRoot": "merkle123...",
      "validatorId": "node1"
    }
  ],
  "length": 2,
  "isValid": true,
  "latestBlockHash": "0000abc123..."
}
```

**cURL Example:**
```bash
curl http://localhost:3000/blockchain
```

---

### 3. Get Transaction by ID

**Endpoint:** `GET /transaction/:transactionId`

**Description:** Retrieve details of a specific transaction.

**Response:**
```json
{
  "success": true,
  "transaction": {
    "id": "txn_123456",
    "from": "farmer1",
    "to": "buyer1",
    "amount": 5000,
    "timestamp": "2025-01-20T10:05:00.000Z",
    "block": {
      "index": 1,
      "hash": "0000abc123...",
      "confirmations": 5
    }
  }
}
```

**cURL Example:**
```bash
curl http://localhost:3000/transaction/txn_123456
```

---

### 4. Get Transactions by Address

**Endpoint:** `GET /address/:address/transactions`

**Description:** Get all transactions for a specific farmer/buyer.

**Response:**
```json
{
  "success": true,
  "address": "farmer1",
  "transactions": [
    {
      "id": "txn_123",
      "from": "farmer1",
      "to": "buyer1",
      "amount": 5000,
      "blockIndex": 1
    },
    {
      "id": "txn_456",
      "from": "buyer2",
      "to": "farmer1",
      "amount": 3000,
      "blockIndex": 3
    }
  ],
  "count": 2
}
```

**cURL Example:**
```bash
curl http://localhost:3000/address/farmer1/transactions
```

---

### 5. Get Blockchain Statistics

**Endpoint:** `GET /stats`

**Description:** Get blockchain statistics and health metrics.

**Response:**
```json
{
  "success": true,
  "stats": {
    "totalBlocks": 42,
    "totalTransactions": 150,
    "miningDifficulty": 2,
    "latestBlockHash": "0000abc123...",
    "chainValid": true,
    "uptime": "2h 30m",
    "distributed": {
      "enabled": true,
      "connectedPeers": 2,
      "validators": 2,
      "nodeId": "node1"
    }
  }
}
```

**cURL Example:**
```bash
curl http://localhost:3000/stats
```

---

### 6. Validate Blockchain

**Endpoint:** `GET /validate`

**Description:** Check if blockchain is valid (all hashes verified).

**Response:**
```json
{
  "success": true,
  "valid": true,
  "message": "Blockchain is valid"
}
```

**cURL Example:**
```bash
curl http://localhost:3000/validate
```

---

## 🔐 Admin Endpoints

**All admin endpoints require header:** `x-admin-key: <your-admin-key>`

### 7. Get Network Status

**Endpoint:** `GET /admin/network/status`

**Description:** Get comprehensive network health and peer information.

**Response:**
```json
{
  "success": true,
  "network": {
    "nodeId": "node1",
    "role": "validator",
    "connectedPeers": 2,
    "totalNodes": 3,
    "validators": ["node1", "node3"],
    "peers": [
      {
        "nodeId": "node2",
        "url": "ws://localhost:6002",
        "status": "active",
        "lastSeen": "2025-01-20T12:30:00.000Z"
      }
    ],
    "blockchainHeight": 42,
    "consensusStatus": "healthy"
  }
}
```

**cURL Example:**
```bash
curl http://localhost:3000/admin/network/status \
  -H "x-admin-key: admin-key-change-this-in-production-SIH2025"
```

---

### 8. List All Nodes

**Endpoint:** `GET /admin/nodes?status=<status>&type=<type>`

**Query Parameters:**
- `status` (optional): `active`, `pending`, `inactive`, `blacklisted`
- `type` (optional): `validator`, `peer`

**Response:**
```json
{
  "success": true,
  "nodes": [
    {
      "id": "node1",
      "url": "ws://localhost:6001",
      "host": "localhost",
      "port": 6001,
      "nodeType": "validator",
      "status": "active",
      "reputation": 100,
      "joinedAt": "2025-01-20T10:00:00.000Z"
    }
  ],
  "total": 3
}
```

**cURL Examples:**
```bash
# All nodes
curl http://localhost:3000/admin/nodes \
  -H "x-admin-key: admin-key-change-this-in-production-SIH2025"

# Only validators
curl http://localhost:3000/admin/nodes?type=validator \
  -H "x-admin-key: admin-key-change-this-in-production-SIH2025"

# Only active nodes
curl http://localhost:3000/admin/nodes?status=active \
  -H "x-admin-key: admin-key-change-this-in-production-SIH2025"
```

---

### 9. Register New Node

**Endpoint:** `POST /admin/nodes/register`

**Description:** Register a new node to the network (requires admin approval).

**Request Body:**
```json
{
  "url": "ws://localhost:6004",
  "host": "localhost",
  "port": 6004,
  "nodeType": "peer"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Node registered successfully",
  "nodeId": "node4",
  "status": "pending",
  "requiresApproval": true
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:3000/admin/nodes/register \
  -H "x-admin-key: admin-key-change-this-in-production-SIH2025" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "ws://localhost:6004",
    "host": "localhost",
    "port": 6004,
    "nodeType": "peer"
  }'
```

---

### 10. Approve Pending Node

**Endpoint:** `POST /admin/nodes/approve/:nodeId`

**Description:** Approve a pending node to join the network.

**Response:**
```json
{
  "success": true,
  "message": "Node approved successfully",
  "nodeId": "node4",
  "status": "active"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:3000/admin/nodes/approve/node4 \
  -H "x-admin-key: admin-key-change-this-in-production-SIH2025"
```

---

### 11. Promote Node to Validator

**Endpoint:** `POST /admin/nodes/promote/:nodeId`

**Description:** Promote a peer node to validator (can create blocks).

**Response:**
```json
{
  "success": true,
  "message": "Node promoted to validator",
  "nodeId": "node2",
  "newRole": "validator"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:3000/admin/nodes/promote/node2 \
  -H "x-admin-key: admin-key-change-this-in-production-SIH2025"
```

---

### 12. Demote Validator to Peer

**Endpoint:** `POST /admin/nodes/demote/:nodeId`

**Description:** Demote a validator back to peer status.

**Response:**
```json
{
  "success": true,
  "message": "Node demoted to peer",
  "nodeId": "node2",
  "newRole": "peer"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:3000/admin/nodes/demote/node2 \
  -H "x-admin-key: admin-key-change-this-in-production-SIH2025"
```

---

### 13. Remove Node from Network

**Endpoint:** `DELETE /admin/nodes/:nodeId`

**Description:** Disconnect and blacklist a node.

**Request Body:**
```json
{
  "reason": "Misbehaving node - invalid blocks"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Node removed and blacklisted",
  "nodeId": "node4",
  "status": "blacklisted",
  "reason": "Misbehaving node - invalid blocks"
}
```

**cURL Example:**
```bash
curl -X DELETE http://localhost:3000/admin/nodes/node4 \
  -H "x-admin-key: admin-key-change-this-in-production-SIH2025" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Misbehaving node"}'
```

---

### 14. Connect to Peer

**Endpoint:** `POST /admin/network/connect`

**Description:** Manually connect to a specific peer node.

**Request Body:**
```json
{
  "url": "ws://remote-node.example.com:6001",
  "nodeId": "remote-node-1"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connected to peer successfully",
  "peer": {
    "nodeId": "remote-node-1",
    "url": "ws://remote-node.example.com:6001",
    "status": "connected"
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:3000/admin/network/connect \
  -H "x-admin-key: admin-key-change-this-in-production-SIH2025" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "ws://localhost:6002",
    "nodeId": "node2"
  }'
```

---

### 15. Synchronize Blockchain

**Endpoint:** `POST /admin/network/sync`

**Description:** Request chain synchronization from all connected peers.

**Response:**
```json
{
  "success": true,
  "message": "Chain synchronization requested",
  "syncedFrom": ["node2", "node3"],
  "newChainLength": 45,
  "consensusReached": true
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:3000/admin/network/sync \
  -H "x-admin-key: admin-key-change-this-in-production-SIH2025"
```

---

### 16. Force Save Blockchain

**Endpoint:** `POST /admin/blockchain/save`

**Description:** Force immediate save to local file and Firebase.

**Response:**
```json
{
  "success": true,
  "message": "Blockchain saved successfully",
  "savedTo": ["local-file", "firebase"],
  "blockCount": 42
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:3000/admin/blockchain/save \
  -H "x-admin-key: admin-key-change-this-in-production-SIH2025"
```

---

### 17. Get Node Details

**Endpoint:** `GET /admin/nodes/:nodeId`

**Description:** Get detailed information about a specific node.

**Response:**
```json
{
  "success": true,
  "node": {
    "id": "node2",
    "url": "ws://localhost:6002",
    "host": "localhost",
    "port": 6002,
    "nodeType": "validator",
    "status": "active",
    "reputation": 98,
    "joinedAt": "2025-01-20T10:00:00.000Z",
    "lastSeen": "2025-01-20T12:30:00.000Z",
    "totalBlocksCreated": 15,
    "totalBlocksValidated": 42
  }
}
```

**cURL Example:**
```bash
curl http://localhost:3000/admin/nodes/node2 \
  -H "x-admin-key: admin-key-change-this-in-production-SIH2025"
```

---

### 18. Broadcast Message to Network

**Endpoint:** `POST /admin/network/broadcast`

**Description:** Send a custom message to all connected peers (for testing).

**Request Body:**
```json
{
  "type": "CUSTOM_MESSAGE",
  "data": {
    "message": "Test broadcast"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Message broadcast to network",
  "recipients": ["node2", "node3"]
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:3000/admin/network/broadcast \
  -H "x-admin-key: admin-key-change-this-in-production-SIH2025" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "CUSTOM_MESSAGE",
    "data": {"message": "Hello network"}
  }'
```

---

## 🛡️ Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message description",
  "code": "ERROR_CODE"
}
```

**Common Error Codes:**
- `UNAUTHORIZED` - Admin key required/invalid
- `NOT_FOUND` - Resource not found
- `INVALID_INPUT` - Validation failed
- `NETWORK_ERROR` - P2P communication failed
- `CONSENSUS_ERROR` - Block validation failed

---

## 📊 Rate Limits

- **Public Endpoints:** 100 requests / 15 minutes per IP
- **Admin Endpoints:** 500 requests / 15 minutes per API key

---

## 🔗 Integration Example (JavaScript)

```javascript
class BlockchainAPI {
  constructor(baseUrl, adminKey = null) {
    this.baseUrl = baseUrl;
    this.adminKey = adminKey;
  }

  async addTransaction(transaction) {
    const response = await fetch(`${this.baseUrl}/transaction/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(transaction)
    });
    return response.json();
  }

  async getBlockchain() {
    const response = await fetch(`${this.baseUrl}/blockchain`);
    return response.json();
  }

  async getNetworkStatus() {
    const response = await fetch(`${this.baseUrl}/admin/network/status`, {
      headers: { 'x-admin-key': this.adminKey }
    });
    return response.json();
  }
}

// Usage
const blockchain = new BlockchainAPI('http://localhost:3000', 'your-admin-key');

// Add transaction
await blockchain.addTransaction({
  from: 'farmer1',
  to: 'buyer1',
  amount: 5000,
  crop: 'Wheat'
});

// Check network
const status = await blockchain.getNetworkStatus();
console.log('Connected peers:', status.network.connectedPeers);
```

---

**For complete distributed blockchain guide, see `DISTRIBUTED-GUIDE.md`**
