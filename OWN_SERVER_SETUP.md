## 🖥️ DEPLOYING ON YOUR OWN SERVER

### Step 1: Prepare Your Server (Windows/Linux)

#### **For Windows Server:**
```powershell
# 1. Install Python 3.11+ from python.org
# 2. Open PowerShell as Administrator
# 3. Navigate to project folder
cd C:\Users\ujju1\Desktop\SIH_PROJECT

# 4. Create virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Verify model file exists
if (Test-Path "yield_prediction_model.pkl") {
    Write-Host "✅ Model file found"
} else {
    Write-Host "❌ Model file missing"
}
```

#### **For Linux Server (Ubuntu/Debian):**
```bash
# 1. SSH into server
ssh user@server_ip

# 2. Install Python and pip
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y

# 3. Clone/copy project files
git clone <your-repo-url> farmer-dashboard
cd farmer-dashboard

# 4. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt
```

---

### Step 2: Run Production Server

#### **Option A: Using Waitress (Windows Recommended)**
```powershell
# Make sure you're in the project folder with venv activated
python run_production.py

# Output should show:
# 🚀 FARMER PROFIT DASHBOARD - PRODUCTION SERVER
# ✅ Server: Waitress (Production WSGI)
# ✅ Host: 0.0.0.0
# ✅ Port: 5000
# ✅ URL: http://localhost:5000
```

#### **Option B: Using Gunicorn (Linux Recommended)**
```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# For background execution (using nohup)
nohup gunicorn -w 4 -b 0.0.0.0:5000 app:app > app.log 2>&1 &

# Check logs
tail -f app.log
```

---

### Step 3: Configure for Server Access

#### **A. Find Your Server IP:**

**Windows:**
```powershell
ipconfig

# Look for:
# IPv4 Address . . . . . . . . . . . : 192.168.x.x
```

**Linux:**
```bash
hostname -I
# or
ip addr | grep "inet "
```

#### **B. Update Firewall (Allow Port 5000):**

**Windows Firewall:**
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Allow Flask Port 5000" `
    -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

**Linux Firewall (UFW):**
```bash
sudo ufw allow 5000
sudo ufw enable
sudo ufw status
```

#### **C. Update Flask App for External Access:**

In `app.py`, ensure Flask listens on all interfaces:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # debug=False for production
```

---

### Step 4: Keep Server Running (Persistent)

#### **Option A: Windows - Task Scheduler**

1. Open **Task Scheduler**
2. Create Basic Task:
   - **Name:** Farmer Dashboard Server
   - **Trigger:** At startup
   - **Action:** Start a program
   - **Program:** `C:\Python311\python.exe`
   - **Arguments:** `C:\path\to\run_production.py`
   - **Start in:** `C:\Users\ujju1\Desktop\SIH_PROJECT`

#### **Option B: Windows - Background Service**

Create `run_as_service.bat`:
```batch
@echo off
cd C:\Users\ujju1\Desktop\SIH_PROJECT
python run_production.py
pause
```

Then use **NSSM** (Non-Sucking Service Manager):
```powershell
# Download NSSM from nssm.cc
# Run as Administrator
nssm install FarmerDashboard "C:\path\to\run_as_service.bat"
nssm start FarmerDashboard

# Check status
nssm status FarmerDashboard

# Stop service
nssm stop FarmerDashboard
```

#### **Option C: Linux - Systemd Service**

Create `/etc/systemd/system/farmer-dashboard.service`:
```ini
[Unit]
Description=Farmer Profit Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/farmer-dashboard
Environment="PATH=/home/ubuntu/farmer-dashboard/venv/bin"
ExecStart=/home/ubuntu/farmer-dashboard/venv/bin/python run_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable it:
```bash
sudo systemctl daemon-reload
sudo systemctl enable farmer-dashboard
sudo systemctl start farmer-dashboard

# Check status
sudo systemctl status farmer-dashboard

# View logs
sudo journalctl -u farmer-dashboard -f
```

#### **Option D: Linux - Supervisor**

Install supervisor:
```bash
sudo apt install supervisor -y
```

Create `/etc/supervisor/conf.d/farmer-dashboard.conf`:
```ini
[program:farmer-dashboard]
command=/home/ubuntu/farmer-dashboard/venv/bin/python /home/ubuntu/farmer-dashboard/run_production.py
directory=/home/ubuntu/farmer-dashboard
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/farmer-dashboard.log
```

Then:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start farmer-dashboard

# Check status
sudo supervisorctl status
```

---

### Step 5: Reverse Proxy Setup (Recommended)

#### **Using Nginx (Linux):**

Install Nginx:
```bash
sudo apt install nginx -y
```

Create `/etc/nginx/sites-available/farmer-dashboard`:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # or your IP address

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for large predictions
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

Enable it:
```bash
sudo ln -s /etc/nginx/sites-available/farmer-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### **Using IIS (Windows):**

1. Install URL Rewrite module for IIS
2. Create new website pointing to project folder
3. Add reverse proxy rule:
   - Pattern: `.*`
   - Rewrite URL: `http://127.0.0.1:5000/{R:0}`

---

### Step 6: SSL/HTTPS Setup (Optional but Recommended)

#### **Linux with Let's Encrypt:**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

#### **Windows with Self-Signed Certificate:**
```powershell
# Generate certificate (valid 365 days)
$cert = New-SelfSignedCertificate -CertStoreLocation cert:\LocalMachine\My `
    -DnsName "localhost", "127.0.0.1" -FriendlyName "FarmerDashboard"

# Export to file
$pwd = ConvertTo-SecureString -String "password" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath ".\cert.pfx" -Password $pwd
```

---

### Step 7: Access Dashboard

#### **Local Access:**
```
http://localhost:5000
```

#### **From Other Machines (Same Network):**
```
http://192.168.x.x:5000
# Replace with your server's actual IP
```

#### **From Internet (If Port Forwarded):**
```
http://your-public-ip:5000
# Or with domain name
http://farmer-dashboard.yourdomain.com
```

---

### Step 8: Monitor & Logs

#### **Windows - Check Process:**
```powershell
Get-Process python | Where-Object {$_.CommandLine -match "app.py|run_production"}
```

#### **Linux - Check Process:**
```bash
ps aux | grep python
# or
pgrep -f "run_production" -l
```

#### **View Recent Logs:**

**Windows (if using file logging):**
```powershell
Get-Content app.log -Tail 50
```

**Linux (with journalctl):**
```bash
sudo journalctl -u farmer-dashboard -n 50
```

---

### Step 9: Scale for Multiple Users

#### **Load Balancing with Nginx:**
```nginx
upstream dashboard {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://dashboard;
    }
}
```

Run multiple instances:
```bash
# Terminal 1
PORT=5000 python run_production.py

# Terminal 2
PORT=5001 python run_production.py

# Terminal 3
PORT=5002 python run_production.py
```

---

### Step 10: Backup & Updates

#### **Regular Backups:**
```bash
# Backup project
tar -czf farmer-dashboard-backup-$(date +%Y%m%d).tar.gz /path/to/farmer-dashboard/

# Backup model
cp yield_prediction_model.pkl yield_prediction_model.backup.pkl
```

#### **Update Application:**
```bash
# Pull latest changes
git pull origin main

# Restart service
sudo systemctl restart farmer-dashboard
# or
nssm restart FarmerDashboard
```

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Port already in use** | `netstat -ano \| findstr :5000` (Windows) or `lsof -i :5000` (Linux), then kill process |
| **Model not found** | Verify `yield_prediction_model.pkl` exists in project root |
| **Permission denied** | Run with `sudo` (Linux) or as Administrator (Windows) |
| **Cannot access from other machine** | Check firewall, ensure Flask listens on `0.0.0.0`, not `127.0.0.1` |
| **Slow response** | Increase workers/threads in `run_production.py` or use Nginx load balancing |
| **Connection refused** | Check if service is running: `systemctl status farmer-dashboard` (Linux) |

---

## ✅ Deployment Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Model file (`yield_prediction_model.pkl`) present in project root
- [ ] Firewall allows port 5000
- [ ] Server can be accessed from other machines
- [ ] Service set to run on startup
- [ ] Logs monitored and backed up
- [ ] SSL certificate installed (if using HTTPS)
- [ ] Load balancing configured (if multiple users)

---

## 📊 Quick Commands Summary

**Start Server:**
```
Windows: python run_production.py
Linux:   gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Check Status:**
```
Windows: Get-Process python
Linux:   systemctl status farmer-dashboard
```

**View Logs:**
```
Windows: Get-Content app.log -Tail 50
Linux:   sudo journalctl -u farmer-dashboard -f
```

**Restart Service:**
```
Windows: nssm restart FarmerDashboard
Linux:   sudo systemctl restart farmer-dashboard
```

**Stop Service:**
```
Windows: nssm stop FarmerDashboard
Linux:   sudo systemctl stop farmer-dashboard
```

---

**Your dashboard is now ready for production deployment! 🚀**
