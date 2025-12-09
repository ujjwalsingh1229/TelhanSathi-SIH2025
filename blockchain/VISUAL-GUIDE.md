# 🎯 Visual Quick-Start Guide

## Your Setup in 5 Minutes

```
START HERE
    │
    ├─ YES to ngrok? (need public access)
    │  └─> Use TWO-TERMINAL setup (this guide)
    │
    └─ NO (local only)
       └─> See START-NODES-GUIDE.md
```

---

## Setup Phase 1: Prerequisites (2 minutes)

```
┌─────────────────────────────────────────────────────┐
│ BEFORE YOU START - DO THESE ONCE                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Step 1: Get ngrok token                             │
│ ├─ Go to: https://dashboard.ngrok.com              │
│ ├─ Sign up or login                                │
│ └─ Copy your Auth Token                            │
│                                                     │
│ Step 2: Update .env file                            │
│ ├─ Open: .env (in this folder)                     │
│ └─ Find: NGROK_AUTH_TOKEN=???                      │
│    └─ Replace with your token                      │
│                                                     │
│ Step 3: Install dependencies                       │
│ └─ Run in terminal: npm install                    │
│                                                     │
│ ✅ Done with setup!                                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Setup Phase 2: Terminal 1 - ngrok (1 minute)

```
┌──────────────────────────────────────────────────┐
│ TERMINAL 1 - ngrok Tunnel                        │
├──────────────────────────────────────────────────┤
│                                                  │
│ Open PowerShell window #1                        │
│ └─ Windows Key + R                              │
│    └─ Type: powershell                          │
│       └─ Enter                                  │
│                                                  │
│ Go to blockchain folder:                        │
│ └─ cd c:\Users\Harsh Pandhe\Desktop\SIH\       │
│    blockchain                                   │
│                                                  │
│ Start ngrok tunnel:                             │
│ └─ .\start-ngrok-tunnel.ps1                     │
│                                                  │
│ Wait for output:                                │
│ ├─ ✅ ngrok found                              │
│ ├─ ✅ Authentication successful                │
│ ├─ 🚀 Starting ngrok tunnel...                │
│ └─ Forwarding: https://aaaa-bbbb-cccc.        │
│    ngrok.io → http://localhost:3010            │
│                                                  │
│ IMPORTANT:                                      │
│ ├─ Copy the URL (https://aaaa-bbbb-cccc...)   │
│ ├─ Keep this terminal OPEN                     │
│ └─ Don't close it!                             │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## Setup Phase 3: Terminal 2 - Node (1 minute)

```
┌──────────────────────────────────────────────────┐
│ TERMINAL 2 - Blockchain Node                     │
├──────────────────────────────────────────────────┤
│                                                  │
│ Open NEW PowerShell window                       │
│ (Keep Terminal 1 open in background)             │
│ └─ Windows Key + R                              │
│    └─ Type: powershell                          │
│       └─ Enter                                  │
│                                                  │
│ Go to blockchain folder:                        │
│ └─ cd c:\Users\Harsh Pandhe\Desktop\SIH\       │
│    blockchain                                   │
│                                                  │
│ Start blockchain node:                          │
│ └─ .\start-node-only.ps1                        │
│                                                  │
│ Wait for output:                                │
│ ├─ ✅ Node.js version: v24.6.0                 │
│ ├─ ✅ All dependencies present                 │
│ ├─ 🚀 Starting blockchain node...             │
│ ├─ ✅ Blockchain initialized successfully     │
│ └─ 📡 Server running on:                      │
│    http://localhost:3010                       │
│                                                  │
│ IMPORTANT:                                      │
│ ├─ Node is now running                         │
│ └─ Keep this terminal OPEN                     │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## Testing Phase (1 minute)

```
┌──────────────────────────────────────────────────┐
│ TEST IT WORKS - Terminal 3                       │
├──────────────────────────────────────────────────┤
│                                                  │
│ Open ANOTHER PowerShell window                   │
│ (Keep both Terminal 1 & 2 open)                  │
│                                                  │
│ Test command:                                   │
│ └─ curl http://localhost:3010/api/health       │
│                                                  │
│ Expected response:                              │
│ └─ {                                            │
│      "status": "healthy",                       │
│      "node": {                                  │
│        "nodeId": "node1",                       │
│        "publicUrl": "http://localhost:3010"   │
│      }                                          │
│    }                                            │
│                                                  │
│ ✅ If you see this: YOUR NODE IS WORKING!      │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## Multi-PC Phase (Share URL)

```
PC 1: You already have it running ✅

PC 2: Set up with PC 1's URL
├─ Get ngrok URL from Terminal 1 on PC 1
│  (Something like: https://aaaa-bbbb-cccc.ngrok.io)
│
├─ Copy .env from PC 1
│  └─ Change: NODE_ID=node2 (or node3, etc.)
│
├─ Add to .env:
│  └─ BOOTSTRAP_NODES=https://aaaa-bbbb-cccc.ngrok.io,node1
│
├─ Run Terminal 1:
│  └─ .\start-ngrok-tunnel.ps1
│
└─ Run Terminal 2:
   └─ .\start-node-only.ps1

✅ Nodes auto-sync!
```

---

## Visual: Screen Layout

```
YOUR COMPUTER SCREEN
┌─────────────────────────────────────────────────────┐
│ Left Side         │         │  Right Side           │
│                   │         │                       │
│ TERMINAL 1        │  REST   │ TERMINAL 2            │
│ (ngrok)           │  BLANK  │ (Node)                │
│                   │         │                       │
│ > .\start-ngrok-  │         │ > .\start-node-only  │
│   tunnel.ps1      │         │   .ps1                │
│                   │         │                       │
│ Forwarding:       │         │ ✅ Blockchain         │
│ https://aaaa...   │         │    initialized        │
│ ngrok.io          │         │                       │
│                   │         │ 📡 Server running:   │
│ Keep this open!   │         │ http://localhost:    │
│                   │         │ 3010                  │
│                   │         │                       │
│ Keep this open!   │         │ Keep this open!       │
└─────────────────────────────────────────────────────┘
```

---

## Command Cheat Sheet

### Terminal 1 (ngrok)
```powershell
# Start
.\start-ngrok-tunnel.ps1

# Stop
CTRL + C

# Restart
.\start-ngrok-tunnel.ps1
```

### Terminal 2 (Node)
```powershell
# Start
.\start-node-only.ps1

# Stop
CTRL + C

# Restart
.\start-node-only.ps1
```

### Terminal 3+ (Testing)
```bash
# Health check
curl http://localhost:3010/api/health

# See all nodes
curl http://localhost:3010/mobile/api/network/nodes

# Send transaction
curl -X POST http://localhost:3010/mobile/api/transaction/send \
  -H "Content-Type: application/json" \
  -d '{"from":"user1","to":"user2","amount":100}'

# Blockchain stats
curl http://localhost:3010/mobile/api/blockchain/stats
```

---

## Troubleshooting Decision Tree

```
Something went wrong?
│
├─ Terminal 1 shows error
│  ├─ "ngrok not found"
│  │  └─ npm install -g ngrok
│  │
│  ├─ "Authentication failed"
│  │  └─ Check NGROK_AUTH_TOKEN in .env
│  │
│  └─ "failed to start tunnel"
│     └─ Check internet, port 3010 free
│
├─ Terminal 2 shows error
│  ├─ "Cannot find module"
│  │  └─ npm install
│  │
│  ├─ "Port already in use"
│  │  └─ netstat -ano | findstr :3010
│  │     taskkill /PID <PID> /F
│  │
│  └─ "Firebase error"
│     └─ Check internet connection
│
└─ Nodes not syncing
   ├─ Check Terminal 1 is still running
   ├─ Check BOOTSTRAP_NODES in PC 2's .env
   └─ Wait 5 seconds for Firebase sync
```

---

## Status Indicators

### ✅ Everything Working
```
Terminal 1 (ngrok):
├─ Forwarding: https://aaaa-bbbb-cccc.ngrok.io
├─ Status: ONLINE
└─ Keep running!

Terminal 2 (Node):
├─ ✅ Blockchain initialized successfully
├─ 📡 Server running on: http://localhost:3010
└─ Keep running!

Terminal 3 (Test):
├─ curl response: { "status": "healthy" ... }
└─ ✅ WORKING!
```

### ❌ Issues to Check
```
Terminal 1 not starting?
├─ ngrok installed? npm install -g ngrok
├─ Token valid? https://dashboard.ngrok.com
└─ Internet working?

Terminal 2 not starting?
├─ Node.js installed? node --version
├─ Dependencies? npm install
└─ Port free? netstat -ano | findstr :3010

Nodes not connecting?
├─ Is Terminal 1 (ngrok) still running?
├─ Is ngrok URL in PC 2's BOOTSTRAP_NODES?
└─ Check Firebase connection
```

---

## Summary

### What You're Running
1. **ngrok tunnel** (Terminal 1) - Makes your local :3010 public
2. **Blockchain node** (Terminal 2) - Your actual blockchain
3. Both together = **Public blockchain network**

### What You Can Do
- ✅ Send transactions
- ✅ View blockchain
- ✅ Connect mobile apps
- ✅ Add more nodes (PC 2, PC 3, etc.)
- ✅ Sync across PCs automatically

### Time Required
- Prerequisites: 2 minutes (one-time)
- Terminal 1: 30 seconds
- Terminal 2: 30 seconds
- Testing: 1 minute
- **Total: ~4 minutes first time**

---

## Next Steps

1. ✅ Get ngrok token
2. ✅ Add to .env
3. ✅ Run Terminal 1: `.\start-ngrok-tunnel.ps1`
4. ✅ Run Terminal 2: `.\start-node-only.ps1`
5. ✅ Test with curl
6. ✅ Share ngrok URL with other PCs
7. ✅ Connect mobile app
8. ✅ Start transacting!

---

**You've got this!** 🚀
