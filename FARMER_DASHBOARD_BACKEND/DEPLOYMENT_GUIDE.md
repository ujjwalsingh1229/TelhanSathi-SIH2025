# Deployment Guide - Farmer Dashboard Backend

## Production Deployment

This guide covers deploying the Farmer Dashboard Backend to production.

## Prerequisites

- Python 3.7+
- PostgreSQL or SQLite3
- Gunicorn or uWSGI (WSGI server)
- Nginx (reverse proxy, optional)
- SSL certificate (for HTTPS)

## 1. Server Preparation

### 1.1 System Dependencies (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y python3.9 python3.9-venv python3-pip
sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y nginx
sudo apt-get install -y sqlite3
```

### 1.2 Create Application User

```bash
sudo useradd -m -s /bin/bash farmer-dashboard
sudo su - farmer-dashboard
```

## 2. Application Setup

### 2.1 Clone/Copy Application

```bash
cd /home/farmer-dashboard
git clone <repository-url> app
cd app/FARMER_DASHBOARD_BACKEND
```

### 2.2 Create Virtual Environment

```bash
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2.3 Initialize Database

**For SQLite:**
```bash
sqlite3 farmer_dashboard.db < database_schema.sql
```

**For PostgreSQL:**
```bash
createdb farmer_dashboard
psql farmer_dashboard < database_schema.sql
```

## 3. Configuration

### 3.1 Update config.py

```python
# Production settings
DATABASE_URI = 'postgresql://user:password@localhost/farmer_dashboard'
# or
DATABASE_URI = 'sqlite:////home/farmer-dashboard/app/FARMER_DASHBOARD_BACKEND/farmer_dashboard.db'

FEATURES = {
    'enable_arima_forecasting': True,
    'enable_recommendations': True,
    'enable_comparative_analysis': True,
    'enable_historical_data_caching': True,
    'enable_database_logging': True
}

# Security
CORS_CONFIG = {
    'origins': ['https://yourdomain.com'],  # Restrict to your domain
    'methods': ['POST', 'GET'],
    'allow_headers': ['Content-Type', 'Authorization']
}

# Performance
PERFORMANCE = {
    'cache_ttl_seconds': 3600,
    'max_forecast_periods': 24,
    'min_historical_data': 12,
    'batch_processing_size': 100
}
```

### 3.2 Environment Variables

Create `.env` file:

```bash
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@localhost/farmer_dashboard
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
LOG_LEVEL=INFO
```

## 4. Running with Gunicorn

### 4.1 Install Gunicorn

```bash
source venv/bin/activate
pip install gunicorn
```

### 4.2 Create Systemd Service

Create `/etc/systemd/system/farmer-dashboard.service`:

```ini
[Unit]
Description=Farmer Dashboard Backend
After=network.target

[Service]
Type=notify
User=farmer-dashboard
WorkingDirectory=/home/farmer-dashboard/app/FARMER_DASHBOARD_BACKEND
Environment="PATH=/home/farmer-dashboard/app/FARMER_DASHBOARD_BACKEND/venv/bin"
ExecStart=/home/farmer-dashboard/app/FARMER_DASHBOARD_BACKEND/venv/bin/gunicorn \
    -w 4 \
    -b 127.0.0.1:5000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4.3 Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable farmer-dashboard
sudo systemctl start farmer-dashboard
sudo systemctl status farmer-dashboard
```

## 5. Nginx Configuration

Create `/etc/nginx/sites-available/farmer-dashboard`:

```nginx
upstream farmer_dashboard {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL Certificate (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    
    # Gzip Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    
    # Proxy Settings
    location / {
        proxy_pass http://farmer_dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://farmer_dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/farmer-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 6. SSL Certificate (Let's Encrypt)

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com
sudo certbot renew --dry-run  # Test auto-renewal
```

## 7. Database Backups

Create backup script `/home/farmer-dashboard/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/farmer-dashboard/backups"
DB_FILE="/home/farmer-dashboard/app/FARMER_DASHBOARD_BACKEND/farmer_dashboard.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp $DB_FILE $BACKUP_DIR/farmer_dashboard_$TIMESTAMP.db
gzip $BACKUP_DIR/farmer_dashboard_$TIMESTAMP.db

# Keep only last 30 days
find $BACKUP_DIR -name "*.db.gz" -mtime +30 -delete
```

Add to crontab:

```bash
crontab -e
# Add: 0 2 * * * /home/farmer-dashboard/backup.sh
```

## 8. Monitoring & Logging

### 8.1 Log Rotation

Create `/etc/logrotate.d/farmer-dashboard`:

```
/var/log/farmer-dashboard/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 farmer-dashboard farmer-dashboard
    sharedscripts
    postrotate
        systemctl reload farmer-dashboard > /dev/null 2>&1 || true
    endscript
}
```

### 8.2 Monitor Service Health

```bash
# Check service status
sudo systemctl status farmer-dashboard

# View logs
sudo journalctl -u farmer-dashboard -f

# Check Nginx status
sudo nginx -t
sudo systemctl status nginx
```

### 8.3 Performance Monitoring

```bash
# CPU and Memory usage
top

# Disk usage
df -h

# Database size
du -sh farmer_dashboard.db

# Request count
tail -f /var/log/nginx/access.log | grep "POST /api"
```

## 9. Health Checks

### 9.1 Endpoint Health Check

```bash
curl https://yourdomain.com/health
# Should return: {"status": "healthy"}

curl https://yourdomain.com/
# Should return service info
```

### 9.2 Setup Monitoring

```bash
# Create health check script
cat > /home/farmer-dashboard/health_check.sh << 'EOF'
#!/bin/bash
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://yourdomain.com/health)
if [ $RESPONSE -eq 200 ]; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed: $RESPONSE"
    systemctl restart farmer-dashboard
fi
EOF

# Add to crontab (every 5 minutes)
*/5 * * * * /home/farmer-dashboard/health_check.sh
```

## 10. Troubleshooting

### Service won't start

```bash
# Check Gunicorn directly
cd /home/farmer-dashboard/app/FARMER_DASHBOARD_BACKEND
source venv/bin/activate
gunicorn -w 4 -b 127.0.0.1:5000 app:app

# Check logs
sudo journalctl -u farmer-dashboard -n 50
```

### Database connection errors

```bash
# Test database connection
psql -U farmer-dashboard -d farmer_dashboard -c "SELECT COUNT(*) FROM farmer_inputs;"

# Check database size
du -sh farmer_dashboard.db
```

### Nginx errors

```bash
# Test configuration
sudo nginx -t

# Check for port conflicts
sudo netstat -tlnp | grep 5000
sudo netstat -tlnp | grep 80
sudo netstat -tlnp | grep 443
```

### High response times

```bash
# Check worker load
top -p $(pgrep -f "gunicorn")

# Check database queries
sqlite3 farmer_dashboard.db "SELECT COUNT(*) FROM profit_results;"

# Monitor network
iftop
```

## 11. Security Hardening

### 11.1 Firewall Rules

```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 11.2 Fail2Ban (Brute Force Protection)

```bash
sudo apt-get install -y fail2ban

# Create /etc/fail2ban/jail.local
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true
```

### 11.3 Regular Updates

```bash
# Check for updates
sudo apt-get update
sudo apt-get upgrade

# Update Python packages
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## 12. Performance Tuning

### 12.1 Gunicorn Workers

```bash
# Recommended: (2 × CPU cores) + 1
# For 4 CPU cores: 9 workers
# For 8 CPU cores: 17 workers

# Update in systemd service:
ExecStart=/path/to/venv/bin/gunicorn -w 9 ...
```

### 12.2 Database Indexing

Already implemented in `database_schema.sql`:
- farmer_name (frequent filters)
- crop_name (common queries)
- created_at (sorting, date ranges)
- input_id (foreign keys)

### 12.3 Connection Pooling

Update config.py:

```python
DATABASE_URI = 'postgresql://user:password@localhost/farmer_dashboard?client_encoding=utf8&connect_timeout=10&pool_size=20&max_overflow=40'
```

## 13. Scaling Considerations

### For High Traffic:

1. **Load Balancing**: Use multiple Gunicorn instances with Nginx
2. **Caching**: Implement Redis for session/forecast caching
3. **Database**: Migrate to PostgreSQL with replication
4. **CDN**: Use CloudFlare for static content and DDoS protection
5. **Monitoring**: Use DataDog, New Relic, or similar

### Docker Deployment:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 14. Maintenance Schedule

- **Daily**: Monitor logs, check service health
- **Weekly**: Review performance metrics, backup verification
- **Monthly**: Security updates, database maintenance
- **Quarterly**: Review capacity, optimize queries
- **Annually**: Forecast model retraining, security audit

## Support

For deployment issues:
1. Check system logs: `sudo journalctl -u farmer-dashboard`
2. Check Nginx logs: `tail -f /var/log/nginx/error.log`
3. Verify database connectivity
4. Run health checks
5. Review configuration in `config.py`

---

**Last Updated**: December 2024  
**Version**: 1.0.0
