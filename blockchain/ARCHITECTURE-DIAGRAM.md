# 📊 System Architecture - Two Terminal Process

## Process Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR COMPUTER                             │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│   TERMINAL 1         │         │   TERMINAL 2         │
│   (ngrok Tunnel)     │         │  (Blockchain Node)   │
│                      │         │                      │
│ .\start-ngrok-      │         │ .\start-node-only   │
│   tunnel.ps1        │         │   .ps1              │
│                      │         │                      │
└──────────────────────┘         └──────────────────────┘
         │                                │
         │                                │
         ├─ Authenticates               ├─ Loads .env
         │  ngrok                       │
         │                              ├─ Starts Node.js
         ├─ Creates tunnel              │
         │  http://localhost:3010       ├─ Connects to local
         │        ↓                      │  ngrok tunnel
         ├─ Public URL:                 │
         │  https://aaaa-bbbb-          ├─ Initializes
         │  cccc.ngrok.io               │  blockchain
         │                              │
         └──────────────────┬───────────┘
                            │
                            ↓
                    ┌─────────────────┐
                    │  Local Network  │
                    │  (localhost)    │
                    │  :3010 (HTTP)   │
                    │  :6001 (P2P)    │
                    └─────────────────┘
                            │
                            ↓
                    ┌─────────────────┐
                    │  ngrok Tunnel   │
                    │  Forwarding     │
                    └─────────────────┘
                            │
                            ↓
                    ┌─────────────────┐
                    │  PUBLIC INTERNET│
                    │  (ngrok servers)│
                    └─────────────────┘
                            │
                            ↓
                    ┌─────────────────┐
                    │  Other Networks │
                    │  (PC 2, PC 3,   │
                    │   Mobile apps)  │
                    └─────────────────┘
```

---

## Terminal 1: ngrok Tunnel Process

```
START
  │
  ├─ Load .env
  │
  ├─ Check ngrok installed
  │
  ├─ Authenticate with ngrok
  │  (NGROK_AUTH_TOKEN)
  │
  ├─ Create tunnel
  │  proto: http
  │  addr: localhost:3010
  │  region: India
  │
  ├─ Display public URL
  │  https://aaaa-bbbb-cccc.ngrok.io
  │
  └─ Keep running ✅
     (User copies URL)
```

---

## Terminal 2: Blockchain Node Process

```
START
  │
  ├─ Check Node.js
  │
  ├─ Load .env
  │  ENABLE_NGROK = false
  │  (ngrok already running)
  │
  ├─ Initialize blockchain
  │
  ├─ Start P2P network
  │  (localhost:6001)
  │
  ├─ Load from Firebase
  │
  ├─ Register in Firebase
  │  node ID: node1
  │  public URL: http://localhost:3010
  │
  ├─ Start Express server
  │  localhost:3010
  │
  └─ Ready for requests ✅
```

---

## Multi-PC Connection Diagram

```
┌──────────────────────────┐
│         PC 1             │
│    (Bootstrap Node)      │
│                          │
│ Terminal 1: ngrok        │
│ URL: https://aaaa...     │
│                          │
│ Terminal 2: node (Node1) │
└──────────────────────────┘
           │
           │ (Copy URL and .env)
           ↓
┌──────────────────────────┐
│         PC 2             │
│   (Connected Node)       │
│                          │
│ .env has:               │
│ BOOTSTRAP_NODES=        │
│   https://aaaa...,node1 │
│                          │
│ Terminal 1: ngrok        │
│ URL: https://xxxx...     │
│                          │
│ Terminal 2: node (Node2) │
└──────────────────────────┘
           │
           │ (Same as PC 2)
           ↓
┌──────────────────────────┐
│         PC 3             │
│   (Connected Node)       │
│                          │
│ Terminal 1: ngrok        │
│ URL: https://wwww...     │
│                          │
│ Terminal 2: node (Node3) │
└──────────────────────────┘

All nodes connected via P2P + Firebase
All synced automatically ✅
```

---

## Data Flow: Transaction

```
User sends transaction from PC 2
        │
        ↓
  curl -X POST /transaction/send

        ↓
Node 2 receives (http://localhost:3010)

        ↓
Node 2 creates block

        ↓
P2P Network (WebSocket)
├─ Node 2 → Node 1 (via ngrok tunnel)
└─ Node 2 → Node 3 (via ngrok tunnel)

        ↓
Firebase Realtime DB
├─ Node 1 saves
├─ Node 2 saves
└─ Node 3 saves

        ↓
All nodes have same blockchain ✅
```

---

## Port Usage

```
Terminal 1 (ngrok):
├─ :3010 ← Listens to local node
├─ :4040 ← Admin UI (http://localhost:4040)
└─ → Internet ← Creates tunnel

Terminal 2 (Node):
├─ :3010 ← HTTP API (Express)
├─ :6001 ← P2P Network (WebSocket)
└─ :6001 → Other nodes (P2P)
```

---

## Configuration Flow

```
.env file
    │
    ├─ NGROK_AUTH_TOKEN
    │  (Used in Terminal 1)
    │
    ├─ NODE_ID = node1
    │  (Used in Terminal 2)
    │
    ├─ PORT = 3010
    │  (TCP port for HTTP)
    │
    ├─ P2P_PORT = 6001
    │  (TCP port for P2P)
    │
    ├─ BOOTSTRAP_NODES
    │  (For connecting to other nodes)
    │  Format: https://url,nodeId
    │
    └─ FIREBASE_DATABASE_URL
       (For syncing blockchain)
```

---

## ngrok Tunnel Internals

```
Local Network
    │
    ├─ Terminal 2 (Node)
    │  localhost:3010
    │
    └─ ngrok tunnel
       (Terminal 1)
           │
           ├─ Listens on local :3010
           ├─ Connects to ngrok.com servers
           ├─ Creates public URL
           │  https://aaaa-bbbb-cccc.ngrok.io
           └─ Forwards traffic:
              public ← → local :3010
```

---

## Sync Mechanism

```
PC 1 (Node 1)
   │
   ├─ Create transaction
   │  (on local :3010)
   │
   └─ P2P WebSocket
      (via ngrok tunnel)
           │
           ├─→ PC 2 (Node 2)
           │   └─ Add to mempool
           │
           ├─→ PC 3 (Node 3)
           │   └─ Add to mempool
           │
           └─ Firebase Realtime DB
              (all nodes write/read)
                   │
                   ├─ Node 1: Save
                   ├─ Node 2: Save
                   └─ Node 3: Save

Result: All nodes have same blockchain ✅
```

---

## Startup Sequence

```
T1: User starts Terminal 1
    ngrok-tunnel.ps1

    Load .env
    Authenticate
    Create tunnel
    Show URL: https://aaaa-bbbb-cccc.ngrok.io
    KEEP RUNNING

T2: User starts Terminal 2
    (new window)
    node-only.ps1

    Load .env
    Initialize blockchain
    Connect to Firebase
    Listen on :3010
    (Connected to ngrok tunnel from T1)

T3: Node is ready
    Accepts requests
    Syncs with other nodes
    Ready for mobile app
```

---

## Service Dependencies

```
Terminal 2 (Node) depends on:
    │
    ├─ Node.js
    │  (Runtime)
    │
    ├─ Express
    │  (Web server)
    │
    ├─ WebSocket (ws)
    │  (P2P communication)
    │
    ├─ Firebase REST API
    │  (Persistence & sync)
    │
    └─ Terminal 1 (ngrok)
       (Public URL tunneling)

Terminal 1 (ngrok) depends on:
    │
    ├─ ngrok binary
    │  (Tunneling tool)
    │
    ├─ .env NGROK_AUTH_TOKEN
    │  (Authentication)
    │
    └─ Internet connection
       (To ngrok servers)
```

---

## Summary

**Terminal 1:** 
- Starts ngrok tunnel
- Creates public URL
- Forwards traffic to :3010

**Terminal 2:**
- Starts blockchain node
- Listens on :3010
- Uses ngrok tunnel from T1
- Syncs with Firebase

**Together:**
- Public blockchain network
- Multi-PC capable
- Auto-sync via Firebase
- P2P communication via WebSocket

**Result:** Distributed blockchain running on your PC(s)! ✅
