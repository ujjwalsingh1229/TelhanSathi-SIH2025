# ⚡ Quick Reference

## 🎯 START NODE (Recommended: 2 Terminals)

### Terminal 1: ngrok Tunnel
```powershell
.\start-ngrok-tunnel.ps1
```
→ Copy the public URL (e.g., https://aaaa-bbbb-cccc.ngrok.io)

### Terminal 2: Blockchain Node
```powershell
.\start-node-only.ps1
```
→ Node is running on http://localhost:3010

**To connect other PCs:**
Add to their `.env`: `BOOTSTRAP_NODES=https://aaaa-bbbb-cccc.ngrok.io,node1`

---

# Full Feature Reference: New Blockchain Features

## 1. Transaction Signatures

### Sign a Transaction (Farmer)
```javascript
const { generateWallet, signTransaction } = require('./blockchain');

// Generate wallet (do once)
const wallet = generateWallet();

// Create transaction
const tx = {
    from: 'farmer123',
    to: 'buyer456',
    amount: 5000,
    crop: 'Wheat'
};

// Sign it
const signature = signTransaction(tx, wallet.privateKey);

// Send with signature
POST /transaction/add
{
    ...tx,
    signature: signature,
    senderPublicKey: wallet.publicKey
}
```

### Verify Signature (Validator)
```javascript
const { verifySignature } = require('./blockchain');

const isValid = verifySignature(tx, signature, publicKey);
if (isValid) {
    // Accept transaction ✅
} else {
    // Reject transaction ❌
}
```

---

## 2. Pure PoA Blocks

### Create & Sign a Block (Validator)
```javascript
// Create block (instant, no mining!)
const block = new Block(Date.now(), transactionData);
block.index = blockchain.chain.length;
blockchain.addBlock(block);  // <1ms! ✅

// Optionally sign block for extra security
block.signBlock(validatorPrivateKey);
```

### Verify Block Signature
```javascript
const isValid = block.verifyBlockSignature(validatorPublicKey);
```

---

## 3. Hash Consistency

### Guaranteed Same Hash Everywhere
```javascript
const stringify = require('fast-json-stable-stringify');

// Node A
const data = { from: 'A', to: 'B', amount: 100 };
const hash1 = sha256(stringify(data));

// Node B (different key order, same data)
const data = { to: 'B', amount: 100, from: 'A' };
const hash2 = sha256(stringify(data));

// hash1 === hash2 ✅ GUARANTEED
```

---

## 4. Split-Brain Recovery

### What Happens
```javascript
// Network splits into two groups
// Both mine blocks for 30 seconds
// Chains are now equal length with different validators

Group A Chain: [Gen] → [B1-validator1] → [B2-validator1]
Group B Chain: [Gen] → [B1-validator2] → [B2-validator2]

// Network rejoins
// Consensus automatically picks one using:
// 1. Longer length (tie: 2 blocks each)
// 2. Validator reputation (validator1: 50 vs validator2: 30)
// 3. Result: Group A wins ✅
```

### Check Resolution Decision
```javascript
const result = consensus.resolveConflict(
    localChain,
    remoteChain,
    remoteNodeId
);

console.log(result);
// {
//   shouldReplace: true,
//   reason: 'Equal length chains - remote validator has higher reputation',
//   tiebreaker: 'validator_reputation',
//   remoteReputation: 50,
//   localReputation: 30
// }
```

---

## API Examples

### Add Transaction with Signature
```bash
curl -X POST http://localhost:3010/transaction/add \
  -H "Content-Type: application/json" \
  -d '{
    "from": "farmer123",
    "to": "buyer456",
    "amount": 5000,
    "crop": "Wheat",
    "quantity": "100 kg",
    "signature": "304502210...",
    "senderPublicKey": "-----BEGIN PUBLIC KEY-----..."
  }'
```

### Response
```json
{
  "success": true,
  "transactionId": "TXN-1702087621234",
  "blockHash": "0029458a129e42d0b2e2...",
  "blockIndex": 5,
  "signatureVerified": true
}
```

### Get Chain (Hashes are now consistent!)
```bash
curl http://localhost:3010/chain | jq '.chain[].hash'
```

---

## Console Logs You'll See

### Pure PoA Block Creation
```
🔐 Block #5 sealed by Authority | Hash: 0029458a129e42d0b2e2... | Validator: node1
✅ Block #5 digitally signed by validator
```

### Transaction Signature Verification
```
✅ Transaction signature verified for farmer123
💰 Transaction added: farmer123 → buyer456 | ₹5000
```

### Split-Brain Resolution
```
[Consensus] Resolving chain conflict...
  Local chain: 5 blocks, validator: node1, reputation: 50
  Remote chain: 5 blocks, validator: node2, reputation: 35
  Decision: Keep local chain (higher reputation)
```

---

## Testing Script

```powershell
# Test Pure PoA (instant block creation)
$time = Measure-Command {
    $body = @{
        from = "farmer123"
        to = "buyer456"
        amount = 5000
        crop = "Wheat"
        quantity = "100 kg"
    } | ConvertTo-Json
    
    Invoke-RestMethod http://localhost:3010/transaction/add `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $body
}

Write-Host "Block created in: $($time.TotalMilliseconds)ms" 
# Should be <10ms ✅
```

---

## Troubleshooting

### Issue: Signature verification failed
```
❌ Invalid transaction signature!
```
**Fix:** Make sure signature matches the exact transaction data (same order, same values)

### Issue: Hash mismatch between nodes
```
Node 1 hash: 123abc...
Node 2 hash: 123def...
```
**Fix:** All nodes should use `fast-json-stable-stringify` for hashing

### Issue: Network doesn't recover from partition
**Check:** Validator reputation scores
```powershell
Invoke-RestMethod http://localhost:3010/admin/network/status
```

---

## Performance Checklist

- ✅ Blocks created in < 1ms (not 50-100ms)
- ✅ CPU usage minimal (not 100% during mining)
- ✅ Hash consistency across all nodes
- ✅ Automatic network partition recovery
- ✅ Optional signature verification working

---

## Security Checklist

- ✅ Private keys never transmitted
- ✅ Signatures verified before accepting transactions
- ✅ Block signatures verify validator identity
- ✅ Hash consistency prevents tampering
- ✅ Network partition recovery is deterministic

---

## Next: Integration with Marketplace

Once you've verified everything works:

1. Generate farmer/buyer wallets
2. Store public keys in your marketplace database
3. Have farmers sign transactions before sending
4. Dashboard verifies signatures automatically
5. All transactions become immutable proof

---

**Ready to test?** Start nodes and check logs! 🚀
