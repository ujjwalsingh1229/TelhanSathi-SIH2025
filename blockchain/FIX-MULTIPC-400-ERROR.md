# 🔧 Multi-PC Setup - FIX FOR 400 ERROR

## Problem

PC 2 shows 400 error when trying to connect to PC 1's ngrok URL.

This happens because:
- PC 2 tries to use the HTTP ngrok URL directly as a WebSocket connection
- WebSocket needs `ws://` or `wss://` URLs, not `https://`
- This causes a 400 Bad Request error

## Solution

**Don't set BOOTSTRAP_NODES for ngrok URLs!** 

Your blockchain has **Firebase-based auto-discovery** which works much better for multi-PC setups via ngrok.

### Option 1: Let Firebase Handle Discovery (RECOMMENDED)

**On PC 2:**
1. DON'T set BOOTSTRAP_NODES
2. Just make sure `.env` has:
   ```env
   ENABLE_DISTRIBUTED=true
   FIREBASE_DATABASE_URL=https://sih2025-72065-default-rtdb.asia-southeast1.firebasedatabase.app
   ```
3. Run both startup scripts

**What happens:**
- PC 2 registers in Firebase
- PC 2 discovers PC 1 from Firebase
- Both nodes sync automatically via Firebase ✅
- No WebSocket connection issues

### Option 2: Connect via WebSocket (If Both PCs on Same Network)

If PC 1 and PC 2 are on the **same local network** (not over internet):

**On PC 2:**
```env
BOOTSTRAP_NODES=ws://[PC1_LOCAL_IP]:6001,node1
```

Replace `[PC1_LOCAL_IP]` with PC 1's local IP (e.g., `192.168.1.100`)

Example:
```env
BOOTSTRAP_NODES=ws://192.168.1.100:6001,node1
```

---

## What to Do Now

### Fix PC 2 Configuration

Edit `.env` on PC 2:

**Remove this line if it exists:**
```
BOOTSTRAP_NODES=https://f603798f127f.ngrok-free.app,node1
```

**Make sure you have:**
```env
ENABLE_DISTRIBUTED=true
FIREBASE_DATABASE_URL=https://sih2025-72065-default-rtdb.asia-southeast1.firebasedatabase.app
```

### Restart PC 2

```powershell
# Kill existing processes
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force

# Terminal 1: Start ngrok
.\start-ngrok-tunnel.ps1

# Terminal 2: Start node (in new window)
.\start-node-only.ps1
```

### Verify Sync

**On PC 1:**
```bash
curl http://localhost:3010/mobile/api/network/nodes
```

Should show both node1 and node2 ✅

---

## How Multi-PC Works (via Firebase)

```
PC 1 (Node 1)
├─ Register in Firebase
│  nodes/registry/node1 = {nodeId, publicUrl, ...}
│
└─ Every 30 seconds: Update heartbeat

       ↓ (Firebase Realtime DB)

PC 2 (Node 2)
├─ Query Firebase for all nodes
├─ Discovers Node 1
├─ Register in Firebase
│  nodes/registry/node2 = {nodeId, publicUrl, ...}
│
└─ Every 30 seconds: Update heartbeat

       ↓ (Both reading/writing to Firebase)

Blockchain Data
├─ All transactions synced via Firebase
├─ All blocks synced via Firebase
└─ Both nodes have identical blockchain ✅
```

---

## Why Firebase is Better

| Method | Pros | Cons |
|--------|------|------|
| **Firebase Discovery** (Recommended) | ✅ No port forwarding needed<br>✅ Works across internet<br>✅ Automatic sync<br>✅ Persistent | Requires Firebase account |
| WebSocket Direct | Works on LAN | ❌ Needs port 6001 open<br>❌ Doesn't work over ngrok<br>❌ Manual config |

---

## Test Commands

After fixing PC 2:

```bash
# From PC 1
curl http://localhost:3010/mobile/api/network/nodes

# Should show:
# {
#   "nodeCount": 2,
#   "nodes": [
#     {"nodeId": "node1", ...},
#     {"nodeId": "node2", ...}
#   ]
# }
```

---

## If Still Getting 400 Error

1. **Double-check .env** - Make sure BOOTSTRAP_NODES is removed or commented out
2. **Restart node** - Kill all node processes and start fresh
3. **Check Firebase** - Make sure Firebase is accessible
4. **Check logs** - Look for "Node registered in Firebase" message

---

## Summary

| Issue | Fix |
|-------|-----|
| PC 2 getting 400 error | Remove BOOTSTRAP_NODES, use Firebase |
| Nodes not seeing each other | Enable ENABLE_DISTRIBUTED=true |
| Firebase not syncing | Check internet connection |
| Still can't connect | Use local IP if on same network |

**Best practice:** Use Firebase for automatic discovery, forget about BOOTSTRAP_NODES! 🎉
