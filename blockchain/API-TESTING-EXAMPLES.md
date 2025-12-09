# API Testing Examples - cURL Commands

## 🌐 Replace NODE_URL with your ngrok URL or localhost:port

```bash
# Examples:
NODE_URL="http://localhost:3010"                    # Local development
NODE_URL="https://xxxx-xxxx-xxxx.ngrok.io"        # ngrok public URL
```

---

## 1️⃣ Health & Status

### Check Node Health
```bash
curl $NODE_URL/mobile/api/health | jq
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1702107600000,
  "node": {
    "id": "node1",
    "isValidator": true,
    "publicUrl": "https://xxxx-xxxx-xxxx.ngrok.io"
  },
  "blockchain": {
    "totalBlocks": 1,
    "totalTransactions": 0,
    "isValid": true
  }
}
```

---

## 2️⃣ Transactions

### Send a Transaction
```bash
curl -X POST $NODE_URL/mobile/api/transaction/send \
  -H "Content-Type: application/json" \
  -d '{
    "from": "farmer_harsh",
    "to": "buyer_priya",
    "amount": 5000,
    "productName": "Wheat",
    "quantity": 100,
    "unit": "kg"
  }' | jq
```

**Response:**
```json
{
  "success": true,
  "message": "Transaction added to pending pool",
  "transaction": {
    "txId": "TXN-1702107600000-abc123",
    "from": "farmer_harsh",
    "to": "buyer_priya",
    "amount": 5000,
    "timestamp": 1702107600000
  }
}
```

### Get Transaction Details
```bash
curl $NODE_URL/mobile/api/transaction/TXN-1702107600000-abc123 | jq
```

### Get User Transactions
```bash
# Get last 20 transactions for a user
curl "$NODE_URL/mobile/api/transactions?userId=farmer_harsh&limit=20" | jq

# With offset (pagination)
curl "$NODE_URL/mobile/api/transactions?userId=farmer_harsh&limit=20&offset=0" | jq
```

**Response:**
```json
{
  "success": true,
  "userId": "farmer_harsh",
  "totalTransactions": 5,
  "transactions": [
    {
      "from": "farmer_harsh",
      "to": "buyer_priya",
      "amount": 5000,
      "productName": "Wheat",
      "quantity": 100,
      "unit": "kg",
      "blockIndex": 1,
      "blockHash": "abc123...",
      "confirmations": 5
    }
  ]
}
```

---

## 3️⃣ Blockchain Data

### Get Blockchain Statistics
```bash
curl $NODE_URL/mobile/api/blockchain/stats | jq
```

**Response:**
```json
{
  "success": true,
  "statistics": {
    "totalBlocks": 10,
    "totalTransactions": 45,
    "chainValid": true,
    "pendingTransactions": 3,
    "averageBlockTime": 250.5
  }
}
```

### Get Latest Blocks
```bash
# Get last 10 blocks
curl "$NODE_URL/mobile/api/blockchain/latest?count=10" | jq

# Get last 5 blocks
curl "$NODE_URL/mobile/api/blockchain/latest?count=5" | jq
```

**Response:**
```json
{
  "success": true,
  "blocks": [
    {
      "index": 9,
      "hash": "abc123def456...",
      "previousHash": "xyz789...",
      "timestamp": 1702107600000,
      "transactionCount": 5,
      "validatorId": "node1"
    }
  ]
}
```

### Verify a Block
```bash
curl "$NODE_URL/mobile/api/blockchain/verify/abc123def456..." | jq
```

**Response:**
```json
{
  "success": true,
  "blockValid": true,
  "chainValid": true,
  "block": {
    "index": 5,
    "hash": "abc123def456...",
    "timestamp": 1702107600000,
    "transactionCount": 3
  }
}
```

---

## 4️⃣ Network & Discovery

### Get All Active Nodes
```bash
curl $NODE_URL/mobile/api/network/nodes | jq
```

**Response:**
```json
{
  "success": true,
  "nodeCount": 3,
  "nodes": [
    {
      "nodeId": "node1",
      "publicUrl": "https://aaaa-bbbb-cccc.ngrok.io",
      "isValidator": true,
      "reputation": 100,
      "lastSeen": 1702107600000
    },
    {
      "nodeId": "node2",
      "publicUrl": "https://xxxx-yyyy-zzzz.ngrok.io",
      "isValidator": false,
      "reputation": 85,
      "lastSeen": 1702107595000
    }
  ]
}
```

### Get Validators
```bash
curl $NODE_URL/mobile/api/network/validators | jq
```

**Response:**
```json
{
  "success": true,
  "validatorCount": 1,
  "validators": [
    {
      "nodeId": "node1",
      "publicUrl": "https://aaaa-bbbb-cccc.ngrok.io",
      "reputation": 100,
      "lastSeen": 1702107600000
    }
  ]
}
```

---

## 5️⃣ User Analytics

### Get User Statistics
```bash
curl $NODE_URL/mobile/api/user/farmer_harsh/stats | jq
```

**Response:**
```json
{
  "success": true,
  "userId": "farmer_harsh",
  "statistics": {
    "transactionsSent": 5,
    "transactionsReceived": 2,
    "totalAmountSent": 25000,
    "totalAmountReceived": 10000,
    "netBalance": -15000
  }
}
```

---

## 6️⃣ Market Feed

### Get Market Activity
```bash
# Get last 50 transactions
curl "$NODE_URL/mobile/api/market/feed?limit=50" | jq

# Get last 10 transactions
curl "$NODE_URL/mobile/api/market/feed?limit=10" | jq
```

**Response:**
```json
{
  "success": true,
  "feedCount": 10,
  "feed": [
    {
      "type": "transaction",
      "from": "farmer_harsh",
      "to": "buyer_priya",
      "amount": 5000,
      "productName": "Wheat",
      "quantity": 100,
      "unit": "kg",
      "timestamp": 1702107600000,
      "blockIndex": 5,
      "blockHash": "abc123def456..."
    }
  ]
}
```

---

## 🧪 Batch Testing Script

### PowerShell Script
```powershell
# Save as test-api.ps1

$NODE_URL = "http://localhost:3010"

function Test-Endpoint {
    param($method, $path, $body = $null)
    
    try {
        $params = @{
            Uri = "$NODE_URL$path"
            Method = $method
            Headers = @{"Content-Type" = "application/json"}
        }
        
        if ($body) {
            $params.Body = $body | ConvertTo-Json
        }
        
        $response = Invoke-RestMethod @params
        Write-Host "✅ $method $path - SUCCESS" -ForegroundColor Green
        return $response
    } catch {
        Write-Host "❌ $method $path - ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

Write-Host "Testing Mobile API Endpoints..." -ForegroundColor Cyan

# Test 1: Health
Test-Endpoint -method GET -path "/mobile/api/health"

# Test 2: Send transaction
$txBody = @{
    from = "user1"
    to = "user2"
    amount = 100
    productName = "Rice"
    quantity = 50
    unit = "kg"
}
Test-Endpoint -method POST -path "/mobile/api/transaction/send" -body $txBody

# Test 3: Get stats
Test-Endpoint -method GET -path "/mobile/api/blockchain/stats"

# Test 4: Get nodes
Test-Endpoint -method GET -path "/mobile/api/network/nodes"

# Test 5: Get feed
Test-Endpoint -method GET -path "/mobile/api/market/feed?limit=10"

# Test 6: User stats
Test-Endpoint -method GET -path "/mobile/api/user/user1/stats"

Write-Host "`nAll tests completed!" -ForegroundColor Green
```

**Run it:**
```bash
.\test-api.ps1
```

---

## 🔍 Debugging Tips

### Pretty Print Response
```bash
curl $NODE_URL/mobile/api/health | jq '.'
```

### Show Response Headers
```bash
curl -i $NODE_URL/mobile/api/health
```

### Show Request & Response
```bash
curl -v $NODE_URL/mobile/api/health
```

### Test ngrok URL
```bash
curl https://xxxx-xxxx-xxxx.ngrok.io/mobile/api/health
```

### Save Response to File
```bash
curl $NODE_URL/mobile/api/blockchain/stats > stats.json
cat stats.json | jq '.'
```

---

## 📊 Performance Testing

### Test Transaction Throughput
```bash
# Send 10 transactions
for ($i=1; $i -le 10; $i++) {
    curl -X POST $NODE_URL/mobile/api/transaction/send \
      -H "Content-Type: application/json" \
      -d "{\"from\": \"user$i\", \"to\": \"buyer1\", \"amount\": 1000}" \
      -o /dev/null -s
    Write-Host "Transaction $i sent"
}
```

### Monitor Block Creation
```bash
# Check stats every 2 seconds
while ($true) {
    $stats = curl -s $NODE_URL/mobile/api/blockchain/stats | jq '.statistics'
    Clear-Host
    Write-Host "Blocks: $($stats.totalBlocks)"
    Write-Host "Transactions: $($stats.totalTransactions)"
    Start-Sleep -Seconds 2
}
```

---

## ⚙️ Common Patterns

### Check if Node is Ready
```bash
$ready = $false
for ($i=0; $i -lt 10; $i++) {
    try {
        $response = Invoke-RestMethod "$NODE_URL/mobile/api/health"
        $ready = $response.status -eq "healthy"
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
```

### Get All User Transactions Across Nodes
```bash
$userId = "farmer_harsh"
foreach ($node in @("http://localhost:3010", "http://localhost:3011", "http://localhost:3012")) {
    try {
        $txns = Invoke-RestMethod "$node/mobile/api/transactions?userId=$userId"
        Write-Host "Node $node: $($txns.totalTransactions) transactions"
    } catch {
        Write-Host "Node $node: Unavailable"
    }
}
```

---

## 📱 Mobile App Integration

### React/React Native
```javascript
const API_URL = 'https://xxxx-xxxx-xxxx.ngrok.io';

async function sendTransaction(from, to, amount) {
  const response = await fetch(`${API_URL}/mobile/api/transaction/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ from, to, amount, productName: 'Product', quantity: 1, unit: 'unit' })
  });
  return response.json();
}

async function getStats() {
  return fetch(`${API_URL}/mobile/api/blockchain/stats`).then(r => r.json());
}
```

### Flutter/Dart
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

const API_URL = 'https://xxxx-xxxx-xxxx.ngrok.io';

Future<Map> sendTransaction(String from, String to, int amount) async {
  final response = await http.post(
    Uri.parse('$API_URL/mobile/api/transaction/send'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'from': from,
      'to': to,
      'amount': amount,
      'productName': 'Product',
      'quantity': 1,
      'unit': 'unit'
    })
  );
  return jsonDecode(response.body);
}
```

---

## ✅ Verification Checklist

Before deploying to production:

- [ ] All endpoints respond with valid JSON
- [ ] Transactions are created successfully
- [ ] Transactions appear in blockchain stats
- [ ] User stats are accurate
- [ ] Market feed shows recent transactions
- [ ] Network discovery finds all nodes
- [ ] ngrok URLs work from external network
- [ ] Firebase data persists after restart
- [ ] Error responses are meaningful
- [ ] Rate limiting works as expected

---

**Last Updated:** December 9, 2025  
**API Version:** 2.0.0  
**All Endpoints Tested:** ✅ YES
