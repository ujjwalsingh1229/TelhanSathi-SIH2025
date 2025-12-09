# 🚀 Blockchain Node Startup Scripts

This folder contains everything you need to run the TelhanSathi Blockchain network.

## 📁 What's What?

### Core Startup Scripts
| Script | Purpose | When to Use |
|--------|---------|------------|
| `start-ngrok-tunnel.ps1` | Starts ngrok tunnel only | Always run FIRST in Terminal 1 |
| `start-node-only.ps1` | Starts blockchain node only | Run SECOND in Terminal 2 |

### Documentation
| File | Content |
|------|---------|
| `TWO-TERMINAL-SETUP.md` | **📖 START HERE** - Complete setup guide |
| `QUICK-REFERENCE.md` | Quick commands and reference |
| `START-NODES-GUIDE.md` | All options and alternatives |
| `NGROK-DEPLOYMENT-GUIDE.md` | Production deployment tips |

### Application Files
| File | Purpose |
|------|---------|
| `app.js` | Main blockchain application |
| `server.js` | Express server setup |
| `blockchain.js` | Core blockchain logic |
| `firebase.js` | Firebase integration |
| `.env` | Configuration (tokens, ports) |

---

## ⚡ Quick Start

### Prerequisites (One-Time)
```bash
# 1. Install Node.js (if not already done)
# Download from https://nodejs.org/

# 2. Get ngrok token
# Go to https://dashboard.ngrok.com and copy your token

# 3. Create/update .env with your token
# Add: NGROK_AUTH_TOKEN=your_token_here

# 4. Install dependencies
npm install
```

### Run Node (2 Terminals)

**Terminal 1:**
```powershell
.\start-ngrok-tunnel.ps1
```

**Terminal 2:** (Open a NEW PowerShell window)
```powershell
.\start-node-only.ps1
```

**Done!** Node is running. ✅

---

## 📱 What Happens?

### Terminal 1 (ngrok)
```
🌐 TelhanSathi Blockchain - ngrok Tunnel
✅ Authentication successful!
🚀 Starting ngrok tunnel...

Forwarding                    https://aaaa-bbbb-cccc.ngrok.io -> http://localhost:3010
```

**You see:** Public URL for your node
**Keep running:** Yes, don't close this!

### Terminal 2 (Node)
```
🚀 TelhanSathi Blockchain - Node 1
✅ Node.js version: v24.6.0
🚀 Starting blockchain node...
✅ Blockchain initialized successfully

📡 Server running on: http://localhost:3010
```

**You see:** Node startup messages
**Keep running:** Yes, this is your blockchain!

---

## 🖥️ Multi-PC Setup

### Share Your Node URL

Once both terminals are running, you have a public URL:
```
https://aaaa-bbbb-cccc.ngrok.io
```

### Other PC Setup

On another computer:

1. Copy the `blockchain` folder
2. Create `.env` with:
   ```
   NGROK_AUTH_TOKEN=your_token
   NODE_ID=node2
   BOOTSTRAP_NODES=https://aaaa-bbbb-cccc.ngrok.io,node1
   ```
3. Run the same two scripts:
   ```
   Terminal 1: .\start-ngrok-tunnel.ps1
   Terminal 2: .\start-node-only.ps1
   ```

**Nodes auto-sync!** ✅

---

## 🧪 Test Your Setup

### Check Node Health
```bash
curl http://localhost:3010/api/health
```

### See All Nodes in Network
```bash
curl http://localhost:3010/mobile/api/network/nodes
```

### Send Test Transaction
```bash
curl -X POST http://localhost:3010/mobile/api/transaction/send \
  -H "Content-Type: application/json" \
  -d '{"from":"user1","to":"user2","amount":100}'
```

### View Blockchain Stats
```bash
curl http://localhost:3010/mobile/api/blockchain/stats
```

---

## 📊 Ports & Configuration

### Default Ports
- **HTTP API:** `3010` (exposed via ngrok to public)
- **P2P Network:** `6001` (local connections)
- **ngrok Admin:** `4040` (view tunnels at http://localhost:4040)

### Configurable in `.env`
```env
NODE_ID=node1              # Node identifier
PORT=3010                  # HTTP API port
P2P_PORT=6001              # P2P network port
NGROK_AUTH_TOKEN=xxx       # From dashboard.ngrok.com
NGROK_REGION=in            # Region (in=India, us=USA, etc.)
BOOTSTRAP_NODES=xxx,node1  # Other nodes to connect to
```

---

## ❌ Common Issues

### "ngrok not found"
```bash
npm install -g ngrok
```

### "NGROK_AUTH_TOKEN not set"
1. Go to https://dashboard.ngrok.com
2. Copy your Auth Token
3. Edit `.env` and add it
4. Try again

### "Port 3010 already in use"
```powershell
# Find what's using it
netstat -ano | findstr :3010

# Kill it (replace PID)
taskkill /PID <PID> /F
```

### "Cannot connect to other nodes"
1. Make sure PC 1's ngrok tunnel is RUNNING
2. Check the ngrok URL is correct in PC 2's `.env`
3. Wait a few seconds for Firebase sync

### "Firebase connection error"
- Check your internet connection
- Firebase might be temporarily down
- Try again in a minute

---

## 🎯 Next Steps

1. **Read** `TWO-TERMINAL-SETUP.md` for detailed instructions
2. **Run** both scripts in separate terminals
3. **Copy** the ngrok public URL
4. **Share** URL with other PCs for multi-PC setup
5. **Test** with curl commands above

---

## 📞 Support

- **Stuck?** Read `TWO-TERMINAL-SETUP.md` troubleshooting section
- **Need help?** Check `START-NODES-GUIDE.md` for alternatives
- **ngrok issues?** See https://ngrok.com/docs
- **Blockchain questions?** Check `NGROK-DEPLOYMENT-GUIDE.md`

---

## ✅ Checklist

- [ ] Node.js installed (v18+)
- [ ] ngrok installed
- [ ] ngrok token in `.env`
- [ ] `npm install` completed
- [ ] Terminal 1: `start-ngrok-tunnel.ps1` running
- [ ] Terminal 2: `start-node-only.ps1` running
- [ ] Can access http://localhost:3010/api/health
- [ ] Have ngrok public URL copied
- [ ] Ready for multi-PC!

---

**You're all set! Happy blockchain building!** 🎉
