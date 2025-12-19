# 🖥️ OWN SERVER DEPLOYMENT - QUICK START

## ⚡ 30-Second Setup (Windows)

### **Step 1: Copy Project Files**
Copy this entire folder to your server (Windows PC/Laptop):
```
C:\FarmerDashboard\
```

### **Step 2: Double-Click to Start**
```
Double-click: START_SERVER.bat
```

That's it! Your server is running.

---

## 📊 Access Your Dashboard

### **Local Computer (Same PC):**
```
Yield Prediction: http://localhost:5000
Forecast Dashboard: http://localhost:5000/forecast
```

### **From Other Computers in Your Network:**
```
First, get your server IP:
1. Run: ipconfig
2. Look for "IPv4 Address:" (usually 192.168.x.x)

Then access from any device:
  http://192.168.x.x:5000
  http://192.168.x.x:5000/forecast
```

### **From Internet (Outside Your Network):**
You'll need to:
1. Configure port forwarding in your router
2. Get your public IP from: whatismyipaddress.com
3. Access: http://YOUR_PUBLIC_IP:5000

---

## 🔧 What's Included

| File | Purpose |
|------|---------|
| `app.py` | Main Flask web application (800+ lines) |
| `forecast_engine.py` | ARIMA forecasting (850 lines) |
| `forecast_dashboard_ui.py` | Dashboard UI (500+ lines) |
| `run_production.py` | Production server launcher |
| `START_SERVER.bat` | One-click Windows startup |
| `yield_prediction_model.pkl` | ML model (trained) |
| `feature_importance.csv` | Feature columns reference |
| `requirements.txt` | Python dependencies |

---

## 📱 Features Deployed

### **Dashboard 1: Yield Prediction** (`http://SERVER:5000`)
- ✅ 9 farmer-friendly input fields
- ✅ Real-time profit calculations
- ✅ 9 output metrics (yield, revenue, profit, ROI, etc.)
- ✅ Mobile responsive design

### **Dashboard 2: Forecast & Recommendations** (`http://SERVER:5000/forecast`)
- ✅ 12-month price forecasts with Charts.js
- ✅ Crop comparison analysis
- ✅ Oilseed crop shift recommendations
- ✅ Market insights and trends

### **API Endpoints** (for developers)
- `POST /api/predict` - Yield prediction
- `GET /api/forecast/<crop>` - Price forecast
- `POST /api/recommend-crop-shift` - Recommendation engine
- `GET /api/market-insights` - Market analysis

---

## 🛠️ Troubleshooting

### **Server Won't Start**
```powershell
# Check Python is installed
python --version

# Check required files exist
dir yield_prediction_model.pkl
dir feature_importance.csv
dir requirements.txt

# Install dependencies manually
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python run_production.py
```

### **Can't Access from Other Computer**
1. Make sure both PCs are on same WiFi network
2. Get server IP: `ipconfig | findstr IPv4`
3. Use that IP in browser: `http://192.168.x.x:5000`
4. Check Windows Firewall isn't blocking port 5000

### **Model File Missing Error**
```
Make sure these files are in the project root:
  ✓ yield_prediction_model.pkl
  ✓ feature_importance.csv
```

### **Port Already in Use**
```powershell
# Find what's using port 5000
netstat -ano | findstr :5000

# Either close that app or use different port:
set PORT=8080
python run_production.py
```

---

## 📈 Performance Tips

1. **For 5-10 Farmers:** START_SERVER.bat is fine
2. **For 10+ Farmers:** Use Windows Service (see below)
3. **For 50+ Farmers:** Consider cloud deployment

### **Run as Windows Service** (Always On)
```powershell
# Install NSSM (Windows service manager)
# Download from: nssm.cc/download

# Install service
nssm install FarmerDashboard "C:\FarmerDashboard\venv\Scripts\python.exe" "C:\FarmerDashboard\run_production.py"

# Start service
nssm start FarmerDashboard

# Stop service
nssm stop FarmerDashboard

# Uninstall service
nssm remove FarmerDashboard
```

---

## 🔐 Security Checklist

- [ ] Firewall configured (port 5000 or forwarded port)
- [ ] Model file protected (read-only permissions)
- [ ] No sensitive data in logs
- [ ] Server behind router with NAT (recommended)
- [ ] Consider HTTPS for internet access (use Nginx reverse proxy)

---

## 📞 Share with Farmers

Once your server is running, share this URL:

```
Yield Prediction Dashboard:
http://YOUR_SERVER_IP:5000

Forecast Dashboard:
http://YOUR_SERVER_IP:5000/forecast

API Documentation:
http://YOUR_SERVER_IP:5000/api
```

---

## ⏸️ Stop Server

Press `Ctrl + C` in the command window or close the window.

To restart: Double-click `START_SERVER.bat` again.

---

## 🚀 Next Steps

1. ✅ Run `START_SERVER.bat`
2. ✅ Open browser to `http://localhost:5000`
3. ✅ Test with sample data
4. ✅ Share IP with farmers
5. ✅ Monitor performance

**Your own server is now ready to serve farmers!**
