# 🎉 NEW: Two-Terminal Node Setup

## What Changed?

Previously: Tried to run ngrok and node together (complex, error-prone)

**Now:** Separate processes - ngrok in Terminal 1, node in Terminal 2 (simple, clear)

---

## New Files Created

### 🚀 Startup Scripts
- **`start-ngrok-tunnel.ps1`** - Start ngrok tunnel FIRST (Terminal 1)
- **`start-node-only.ps1`** - Start blockchain node SECOND (Terminal 2)

### 📖 Documentation
- **`TWO-TERMINAL-SETUP.md`** - Complete setup guide (START HERE!)
- **`README-SCRIPTS.md`** - Script reference and explanation
- **`INDEX.md`** - Documentation index and navigation
- **`QUICK-REFERENCE.md`** - Updated with quick start

---

## How to Use

### Step 1: Terminal 1
```bash
.\start-ngrok-tunnel.ps1
```

See output:
```
Forwarding    https://aaaa-bbbb-cccc.ngrok.io -> http://localhost:3010
```

**Copy this URL!** Keep terminal running.

### Step 2: Terminal 2 (new window)
```bash
.\start-node-only.ps1
```

See output:
```
✅ Blockchain initialized successfully
📡 Server running on: http://localhost:3010
```

**Done!** Node is running. ✅

---

## Why This Is Better

| Aspect | Old Way | New Way |
|--------|---------|---------|
| **Complexity** | ngrok + node automatic | ngrok separate, node separate |
| **Errors** | Hard to debug | See each process clearly |
| **Control** | No manual intervention | Full control, see public URL |
| **Multi-PC** | Share config | Share simple ngrok URL |
| **Troubleshooting** | Mixed logs | Clean separated logs |

---

## For Multi-PC

### PC 1
```bash
# Terminal 1
.\start-ngrok-tunnel.ps1
→ Get URL: https://aaaa-bbbb-cccc.ngrok.io

# Terminal 2
.\start-node-only.ps1
```

### PC 2 (Send URL from PC 1)
Edit `.env`:
```env
BOOTSTRAP_NODES=https://aaaa-bbbb-cccc.ngrok.io,node1
```

Then:
```bash
# Terminal 1
.\start-ngrok-tunnel.ps1

# Terminal 2
.\start-node-only.ps1
```

**Nodes auto-sync!** ✅

---

## What You Need

**Before starting:**
1. ngrok token in `.env`
2. Run `npm install`
3. Two PowerShell windows open

**That's it!**

---

## Quick Test

```bash
# In another terminal
curl http://localhost:3010/api/health
```

Response:
```json
{ "status": "healthy", "node": { "nodeId": "node1" } }
```

---

## Updated Files

### Modified
- `.env` - Added comments about new process
- `QUICK-REFERENCE.md` - Added new quick start
- `START-NODES-GUIDE.md` - Added reference to new setup

### Created
- `start-ngrok-tunnel.ps1` - ngrok only
- `start-node-only.ps1` - node only
- `TWO-TERMINAL-SETUP.md` - Complete guide
- `README-SCRIPTS.md` - Script explanation
- `INDEX.md` - Documentation navigator

---

## Old Scripts Still Work

The old `start-ngrok-node1.ps1` etc. still exist but are **deprecated**. Use the new two-terminal approach instead.

---

## Where to Go

1. **Quick start?** → `TWO-TERMINAL-SETUP.md`
2. **Just need commands?** → `QUICK-REFERENCE.md`
3. **Understand scripts?** → `README-SCRIPTS.md`
4. **Lost?** → `INDEX.md`

---

## Summary

✅ Created two separate, simple startup scripts
✅ User manually starts ngrok, sees public URL
✅ User manually starts node in separate terminal
✅ Clear separation of concerns
✅ Easy to debug and troubleshoot
✅ Perfect for sharing URLs between PCs
✅ Complete documentation

**This is much better!** 🎉
