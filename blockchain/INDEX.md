# 📚 Documentation Index

## 🎯 Choose Your Path

### I want to START A NODE NOW
**→ Read:** `TWO-TERMINAL-SETUP.md` (5 minutes)

Quick version:
```bash
# Terminal 1
.\start-ngrok-tunnel.ps1

# Terminal 2
.\start-node-only.ps1
```

---

### I want QUICK REFERENCE
**→ Read:** `QUICK-REFERENCE.md` (1 minute)

Essential commands and troubleshooting.

---

### I want ALL OPTIONS & DETAILS
**→ Read:** `START-NODES-GUIDE.md` (10 minutes)

- Local testing (1 node)
- Local testing (3 nodes)
- Multi-PC setup
- Mobile app integration
- Full troubleshooting

---

### I want to UNDERSTAND THE SCRIPTS
**→ Read:** `README-SCRIPTS.md` (5 minutes)

- What each script does
- File structure
- Configuration options
- Common issues

---

### I want PRODUCTION DEPLOYMENT
**→ Read:** `NGROK-DEPLOYMENT-GUIDE.md`

- Cloud deployment
- Security considerations
- Scaling multiple nodes
- Monitoring & logs

---

## 📂 File Organization

### 🚀 Startup Scripts (Use These!)
```
start-ngrok-tunnel.ps1      ← Terminal 1: ngrok tunnel
start-node-only.ps1         ← Terminal 2: blockchain node
```

### 📖 Documentation
```
TWO-TERMINAL-SETUP.md       ← START HERE (recommended)
QUICK-REFERENCE.md          ← Cheat sheet
START-NODES-GUIDE.md        ← All options
README-SCRIPTS.md           ← Script explanation
NGROK-DEPLOYMENT-GUIDE.md   ← Production tips
API-TESTING-EXAMPLES.md     ← API usage examples
```

### 🔧 Configuration
```
.env                        ← Token, ports, settings
```

### 💻 Application Code
```
app.js                      ← Main entry point
server.js                   ← Express setup
blockchain.js              ← Core blockchain
firebase.js                ← Firebase integration
ngrok-manager.js           ← ngrok tunnel management
firebase-discovery.js      ← Node discovery
mobile-api.js              ← Mobile API endpoints
```

---

## ⚡ Five-Minute Quickstart

### Step 1: One-Time Setup (2 minutes)
```bash
# Get ngrok token from https://dashboard.ngrok.com
# Add to .env:
# NGROK_AUTH_TOKEN=your_token_here

npm install
```

### Step 2: Terminal 1 (30 seconds)
```bash
.\start-ngrok-tunnel.ps1
# Copy the public URL shown
```

### Step 3: Terminal 2 (30 seconds)
```bash
.\start-node-only.ps1
# Node is running!
```

### Step 4: Test (1 minute)
```bash
curl http://localhost:3010/api/health
```

**Done!** ✅

---

## 🖥️ Multi-PC (10 minutes total)

| PC | Step 1 | Step 2 | Step 3 |
|----|--------|--------|--------|
| PC 1 | Run `start-ngrok-tunnel.ps1` | Get URL | Run `start-node-only.ps1` |
| PC 2 | Add to `.env`: `BOOTSTRAP_NODES=PC1_URL,node1` | Run `start-ngrok-tunnel.ps1` | Run `start-node-only.ps1` |
| PC 3 | Same as PC 2 | Run `start-ngrok-tunnel.ps1` | Run `start-node-only.ps1` |

**Nodes auto-sync!** ✅

---

## 🧪 Verify Everything Works

### Test 1: Node Health (30 seconds)
```bash
curl http://localhost:3010/api/health
```

Response:
```json
{ "status": "healthy", "node": { "nodeId": "node1" } }
```

### Test 2: Network Status (30 seconds)
```bash
curl http://localhost:3010/mobile/api/network/nodes
```

### Test 3: Send Transaction (1 minute)
```bash
curl -X POST http://localhost:3010/mobile/api/transaction/send \
  -H "Content-Type: application/json" \
  -d '{"from":"user1","to":"user2","amount":100}'
```

### Test 4: View Dashboard (1 minute)
Open browser: `http://localhost:3010`

---

## 📋 Common Tasks

### I want to...

**...start a node**
→ `TWO-TERMINAL-SETUP.md` Section "Quick Start"

**...connect another PC**
→ `TWO-TERMINAL-SETUP.md` Section "Multi-PC Setup"

**...send a transaction**
→ `API-TESTING-EXAMPLES.md` or `QUICK-REFERENCE.md`

**...see blockchain stats**
→ Run: `curl http://localhost:3010/mobile/api/blockchain/stats`

**...see all nodes**
→ Run: `curl http://localhost:3010/mobile/api/network/nodes`

**...stop the node**
→ Terminal: Press `CTRL + C`

**...check ngrok status**
→ Open browser: `http://localhost:4040`

**...test on mobile app**
→ Use ngrok URL: `https://aaaa-bbbb-cccc.ngrok.io`

**...troubleshoot**
→ `QUICK-REFERENCE.md` Section "Troubleshooting"

---

## 🎓 Learning Path

### Beginner (Just Want It Running)
1. Read: `TWO-TERMINAL-SETUP.md`
2. Run: Both startup scripts
3. Test: `curl http://localhost:3010/api/health`
4. Done! ✅

### Intermediate (Want to Understand)
1. Read: `README-SCRIPTS.md`
2. Read: `QUICK-REFERENCE.md`
3. Run multi-PC setup
4. Test with `API-TESTING-EXAMPLES.md`

### Advanced (Want Full Details)
1. Read: All documentation files
2. Study: Core code (`blockchain.js`, `server.js`)
3. Customize: Configuration in `.env`
4. Deploy: `NGROK-DEPLOYMENT-GUIDE.md`

---

## ✅ Pre-Flight Checklist

Before running scripts:

- [ ] Node.js v18+ installed? → `node --version`
- [ ] ngrok installed? → `ngrok --version`
- [ ] ngrok token in `.env`? → Check `.env` file
- [ ] Dependencies installed? → `npm install`
- [ ] Port 3010 available? → `netstat -ano | findstr :3010`

---

## 🚨 Quick Troubleshooting

| Issue | Solution | Read More |
|-------|----------|-----------|
| "ngrok not found" | `npm install -g ngrok` | `README-SCRIPTS.md` |
| "NGROK_AUTH_TOKEN not set" | Add to `.env` | `TWO-TERMINAL-SETUP.md` |
| "Port already in use" | Kill process or use different port | `QUICK-REFERENCE.md` |
| "Cannot connect to other nodes" | Check PC 1's ngrok is running | `TWO-TERMINAL-SETUP.md` |
| "Firebase error" | Check internet, might be down | `QUICK-REFERENCE.md` |

---

## 🔗 External Resources

- **ngrok dashboard:** https://dashboard.ngrok.com
- **ngrok docs:** https://ngrok.com/docs
- **Firebase console:** https://console.firebase.google.com
- **Node.js:** https://nodejs.org/

---

## 📞 Need Help?

1. **Quick answer?** → `QUICK-REFERENCE.md`
2. **Setup issues?** → `TWO-TERMINAL-SETUP.md` troubleshooting
3. **Script questions?** → `README-SCRIPTS.md`
4. **API questions?** → `API-TESTING-EXAMPLES.md`
5. **Production?** → `NGROK-DEPLOYMENT-GUIDE.md`

---

## 🎯 You Are Here

You're reading the **documentation index**. 

**Next step:** Pick a path above and start reading! ⬆️

---

**Happy building!** 🚀
