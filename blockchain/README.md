# 🌾 TelhanSathi Agricultural Blockchain System

**Production-Ready Blockchain for Agricultural Marketplace (SIH 2025)**

A secure, scalable blockchain implementation for tracking agricultural transactions, contracts, and payments with immutable records and real-time transparency.

---

## 🚀 Features

### ✅ **Production Security**
- **JWT Authentication** - Secure token-based auth for mobile apps
- **Rate Limiting** - API abuse prevention (100 req/15min, 10 write ops/min)
- **Input Validation** - Joi schema validation for all inputs
- **Helmet Security Headers** - Protection against common web vulnerabilities
- **CORS Configuration** - Restricted cross-origin access
- **XSS Prevention** - Input sanitization with validator.js

### 🔗 **Blockchain Core**
- **SHA-256 Hashing** - Cryptographic block integrity
- **Proof of Work** - Mining with configurable difficulty
- **Merkle Roots** - Transaction data integrity verification
- **Chain Validation** - Automatic integrity checks
- **Transaction Pool** - In-memory transaction indexing

### 💾 **Firebase Integration**
- **Real-time Database** - Persistent blockchain storage
- **Auto-sync** - Automatic saves after each block
- **Disaster Recovery** - Auto-load from Firebase on restart
- **Transaction Indexing** - Quick lookup by transaction ID

### 📱 **Mobile API Endpoints**
- `/api/mobile/transactions` - User transaction history (paginated)
- `/api/mobile/stats/:userId` - User statistics & analytics
- `/api/mobile/verify/:txId` - Transaction verification
- `/api/mobile/feed` - Recent marketplace activity

---

## 📦 Installation

### Prerequisites
- Node.js 14+ 
- Firebase account with Realtime Database

### Quick Start

```powershell
# 1. Clone or navigate to the project
cd blockchain

# 2. Install dependencies
npm install

# 3. Configure environment variables
cp .env.example .env
# Edit .env with your Firebase credentials

# 4. Start the server
npm start
```

Server will run on: **http://localhost:3000**

---

## 🔐 Environment Configuration

Create a `.env` file with these variables:

```env
# Server
PORT=3000
NODE_ENV=production

# Firebase (Get from Firebase Console)
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_DATABASE_URL=https://your-db.region.firebasedatabase.app

# Security
JWT_SECRET=your-super-secret-jwt-key-CHANGE-THIS
JWT_EXPIRY=24h

# Blockchain
MINING_DIFFICULTY=2
MINING_REWARD=50

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# CORS (Add your mobile app domains)
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

**⚠️ IMPORTANT**: Change `JWT_SECRET` and `ADMIN_API_KEY` in production!

---

## 📡 API Documentation

### Authentication

#### **POST** `/auth/login`
Generate JWT token for API access.

```json
{
  "userId": "farmer_123",
  "role": "farmer",
  "name": "Ram Kumar"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "userId": "farmer_123",
    "role": "farmer",
    "name": "Ram Kumar"
  },
  "expiresIn": "24h"
}
```

#### **GET** `/auth/verify`
Verify token validity (requires Authorization header).

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

### Blockchain Operations

#### **POST** `/transaction/add`
Add a new transaction to the blockchain.

**Body:**
```json
{
  "from": "farmer_ram_123",
  "to": "buyer_fpo_456",
  "amount": 25000,
  "crop": "Wheat",
  "quantity": "500 kg",
  "upiTransactionId": "UPI123456789",
  "location": "Pune APMC Mandi"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Transaction added to blockchain",
  "transactionId": "UPI123456789",
  "contractId": "CONTRACT-1234567890",
  "blockHash": "009c296afe016e2882d2...",
  "blockIndex": 1
}
```

#### **POST** `/contract/create`
Create a new farming contract.

**Body:**
```json
{
  "contractId": "CONTRACT-001",
  "farmerId": "F123",
  "farmerName": "Ram Kumar",
  "farmerPhone": "9876543210",
  "buyerId": "B456",
  "buyerName": "FPO Pune",
  "buyerPhone": "9123456789",
  "crop": "Wheat",
  "variety": "HD-2967",
  "quantity": 1000,
  "unit": "kg",
  "pricePerUnit": 25,
  "totalAmount": 25000,
  "advanceAmount": 5000,
  "expectedDeliveryDate": "2025-12-15",
  "location": "Pune"
}
```

#### **POST** `/contract/pay`
Record payment for a contract.

**Body:**
```json
{
  "contractId": "CONTRACT-001",
  "amount": 20000,
  "paymentMode": "UPI",
  "upiTransactionId": "UPI987654321"
}
```

#### **GET** `/chain`
View entire blockchain (for transparency).

**Response:**
```json
{
  "length": 5,
  "isValid": true,
  "chain": [
    {
      "index": 0,
      "timestamp": 1733655600000,
      "data": {...},
      "hash": "7804646956a2ff86317d...",
      "previousHash": "0"
    }
  ]
}
```

#### **GET** `/transaction/:id`
Get transaction details by ID.

#### **GET** `/contract/:id`
Get contract details and history.

#### **GET** `/user/:userId/transactions?role=farmer`
Get all transactions for a user.

#### **GET** `/stats`
Get blockchain statistics.

**Response:**
```json
{
  "success": true,
  "statistics": {
    "totalBlocks": 10,
    "totalContracts": 5,
    "totalTransactions": 8,
    "totalValue": "125000.00",
    "topCrops": [["Wheat", 3], ["Rice", 2]],
    "activeFarmers": 4,
    "activeBuyers": 3,
    "chainValid": true
  }
}
```

---

### Mobile API

#### **GET** `/api/health`
System health check.

#### **GET** `/api/mobile/transactions?userId=F123&page=1&limit=20`
Get paginated user transactions.

#### **GET** `/api/mobile/stats/:userId`
Get user-specific statistics.

#### **GET** `/api/mobile/verify/:txId`
Verify transaction on blockchain.

#### **GET** `/api/mobile/feed`
Get recent marketplace activity feed.

---

## 🔒 Security Features

### Rate Limiting
```javascript
// General API: 100 requests per 15 minutes
// Write operations: 10 requests per minute
```

### Input Validation
All inputs are validated using Joi schemas:
- Transaction: from, to, amount, crop, quantity
- Contract: All contract fields with type checking
- Payment: amount, payment mode, reference IDs

### CORS Policy
Only whitelisted domains can access the API. Configure in `.env`:
```env
ALLOWED_ORIGINS=http://localhost:3000,https://app.yoursite.com
```

### JWT Authentication
Protected endpoints require Bearer token:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:3000/auth/verify
```

---

## 🛠️ Testing

### Test Authentication
```powershell
curl -X POST http://localhost:3000/auth/login `
  -H "Content-Type: application/json" `
  -d '{"userId":"test_user","role":"farmer","name":"Test Farmer"}'
```

### Test Transaction (with token)
```powershell
$token = "YOUR_JWT_TOKEN"
curl -X POST http://localhost:3000/transaction/add `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $token" `
  -d '{"from":"farmer1","to":"buyer1","amount":10000,"crop":"Rice","quantity":"100kg"}'
```

### View Blockchain
```powershell
curl http://localhost:3000/chain
```

---

## 📊 Monitoring

The system provides comprehensive logging:

```
[2025-12-08T10:30:00.000Z] POST /transaction/add - IP: ::1
📥 NEW TRANSACTION REQUEST
✅ Validation passed
⛏️  Mining block with difficulty 2...
✅ Block #1 mined in 6ms | Hash: 009c296...
💾 Saving blockchain to Firebase...
✅ Firebase save successful
```

---

## 🚨 Error Handling

### Common Errors

**401 Unauthorized**
```json
{
  "error": "Access token required"
}
```

**400 Validation Error**
```json
{
  "success": false,
  "error": "Validation failed",
  "details": [
    {
      "field": "amount",
      "message": "\"amount\" must be a positive number"
    }
  ]
}
```

**429 Too Many Requests**
```json
{
  "error": "Too many requests from this IP, please try again later.",
  "retryAfter": "15 minutes"
}
```

---

## 📁 Project Structure

```
blockchain/
├── telhan_chain.js        # Main blockchain server with security
├── dashboard.html         # Modern web dashboard UI
├── package.json           # Dependencies
├── .env                   # Environment variables (DO NOT COMMIT)
├── .env.example          # Template for .env
├── .gitignore            # Git ignore rules
├── test-security.ps1     # Security test suite
├── README.md             # This file
└── SECURITY-IMPLEMENTATION.md  # Security test results
```

---

## 🔄 Deployment

### Production Checklist

- [ ] Change `JWT_SECRET` to a strong random value
- [ ] Change `ADMIN_API_KEY` to a secure key
- [ ] Set `NODE_ENV=production`
- [ ] Configure Firebase security rules
- [ ] Update `ALLOWED_ORIGINS` with your production domains
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure firewall rules
- [ ] Set up monitoring/logging service
- [ ] Enable Firebase backup

### Firebase Security Rules

Set these rules in Firebase Console:

```json
{
  "rules": {
    "blockchain": {
      ".read": "auth != null",
      ".write": "auth != null"
    },
    "transactions": {
      ".read": "auth != null",
      ".write": "auth != null"
    }
  }
}
```

---

## 📈 Performance

- **Mining Speed**: ~6ms per block (difficulty 2)
- **Chain Validation**: O(n) complexity, ~1ms for 100 blocks
- **Firebase Sync**: Async, non-blocking operations
- **Transaction Lookup**: O(1) with Map-based pool

---

## 🐛 Troubleshooting

### Server won't start
```powershell
# Check if port 3000 is in use
Get-NetTCPConnection -LocalPort 3000

# Kill the process using the port
Stop-Process -Id <PID> -Force
```

### Firebase connection errors
- Verify `.env` has correct Firebase credentials
- Check Firebase database URL includes region (e.g., `asia-southeast1`)
- Ensure Firebase Realtime Database is enabled in console

### Rate limit errors
- Wait 15 minutes for general API limits to reset
- Reduce request frequency for write operations

---

## 📞 Support

For SIH 2025 queries:
- **Project**: TelhanSathi Agricultural Marketplace
- **Team**: [Your Team Name]
- **Technology**: Node.js, Express, Firebase, Blockchain

---

## 📄 License

MIT License - Feel free to use for SIH 2025 and beyond!

---

**Built with ❤️ for Indian Farmers** 🌾
