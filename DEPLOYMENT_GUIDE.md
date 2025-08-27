# PerspectiveUPSC - Manual Deployment Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Server Setup](#initial-server-setup)
3. [Code Deployment from GitHub](#code-deployment-from-github)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [Dependencies Installation](#dependencies-installation)
7. [Service Configuration](#service-configuration)
8. [Application Startup](#application-startup)
9. [Domain Configuration](#domain-configuration)
10. [Troubleshooting](#troubleshooting)
11. [Updates & Maintenance](#updates--maintenance)

---

## 🔧 Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04+ / CentOS 7+ / RHEL 8+
- **RAM**: Minimum 2GB (Recommended: 4GB+)
- **Storage**: Minimum 20GB SSD
- **CPU**: 2+ cores recommended
- **Network**: Public IP address and domain name

### Required Software
- **Node.js**: Version 18+ 
- **Python**: Version 3.11+
- **MongoDB**: Version 4.4+
- **Nginx**: For reverse proxy
- **PM2**: For process management
- **Git**: For code deployment

---

## 🖥️ Initial Server Setup

### 1. Update System
```bash
# For Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# For CentOS/RHEL
sudo yum update -y
```

### 2. Install Node.js
```bash
# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version

# Install Yarn
npm install -g yarn
```

### 3. Install Python 3.11
```bash
# For Ubuntu
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Create symlink
sudo ln -sf /usr/bin/python3.11 /usr/bin/python3

# Verify installation
python3 --version
pip3 --version
```

### 4. Install MongoDB
```bash
# Import MongoDB GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list

# Install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start and enable MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify installation
sudo systemctl status mongod
```

### 5. Install Nginx
```bash
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 6. Install PM2
```bash
npm install -g pm2
```

---

## 📥 Code Deployment from GitHub

### 1. Clone Repository
```bash
# Navigate to your preferred directory
cd /var/www/

# Clone your repository
sudo git clone https://github.com/YOUR_USERNAME/perspectiveupsc.git
cd perspectiveupsc

# Set proper permissions
sudo chown -R $USER:$USER /var/www/perspectiveupsc
```

### 2. Setup Git for Updates
```bash
# Configure git for easy updates
git config pull.rebase false
git branch --set-upstream-to=origin/main main
```

---

## ⚙️ Environment Configuration

### 1. Backend Environment Setup
```bash
cd /var/www/perspectiveupsc/backend

# Create environment file
sudo nano .env
```

**Backend .env Configuration:**
```env
# Database Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=perspectiveupsc_prod
CORS_ORIGINS=https://perspectiveupsc.com,https://www.perspectiveupsc.com

# Security
SECRET_KEY=your-super-secure-secret-key-change-this-in-production-32-chars-long

# Email Configuration (GoDaddy Titan)
SMTP_SERVER=smtpout.secureserver.net
SMTP_PORT=587
SMTP_USERNAME=admin@perspectiveupsc.com
SMTP_PASSWORD=Perspective@2025
FROM_EMAIL=admin@perspectiveupsc.com

# Payment Gateway (Razorpay LIVE keys)
RAZORPAY_KEY_ID=rzp_live_YOUR_LIVE_KEY_ID
RAZORPAY_KEY_SECRET=your_live_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# Application Settings
ENV=production
DEBUG=false
```

### 2. Frontend Environment Setup
```bash
cd /var/www/perspectiveupsc/frontend

# Create environment file
sudo nano .env
```

**Frontend .env Configuration:**
```env
# Backend API URL (your domain)
REACT_APP_BACKEND_URL=https://perspectiveupsc.com

# WebSocket configuration
WDS_SOCKET_PORT=443

# Build optimization
GENERATE_SOURCEMAP=false
```

---

## 💾 Database Setup

### 1. Create MongoDB Database
```bash
# Connect to MongoDB
mongo

# Create database and user
use perspectiveupsc_prod

# Create admin user for database
db.createUser({
  user: "perspectiveupsc_admin",
  pwd: "your_secure_database_password",
  roles: [
    { role: "readWrite", db: "perspectiveupsc_prod" }
  ]
})

# Exit MongoDB shell
exit
```

### 2. Update MongoDB Connection
```bash
# Edit backend .env to use authenticated connection
MONGO_URL=mongodb://perspectiveupsc_admin:your_secure_database_password@localhost:27017/perspectiveupsc_prod
```

### 3. Initialize Default Admin User
Create a script to add the default admin user:

```bash
cd /var/www/perspectiveupsc/backend
nano init_admin.py
```

**init_admin.py:**
```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import uuid
from datetime import datetime, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    client = AsyncIOMotorClient("mongodb://perspectiveupsc_admin:your_secure_database_password@localhost:27017/perspectiveupsc_prod")
    db = client.perspectiveupsc_prod
    
    # Check if admin exists
    existing_admin = await db.users.find_one({"email": "perspectiveupsc1@gmail.com"})
    
    if not existing_admin:
        # Create admin user
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": "perspectiveupsc1@gmail.com",
            "name": "Perspective UPSC Admin",
            "password_hash": pwd_context.hash("perspective@2025"),
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.users.insert_one(admin_user)
        print("✅ Admin user created successfully")
    else:
        print("ℹ️ Admin user already exists")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin())
```

Run the script:
```bash
python3 init_admin.py
```

---

## 📦 Dependencies Installation

### 1. Backend Dependencies
```bash
cd /var/www/perspectiveupsc/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed successfully')"
```

### 2. Frontend Dependencies
```bash
cd /var/www/perspectiveupsc/frontend

# Install dependencies
yarn install

# Build production version
yarn build

# Verify build
ls -la build/
```

---

## 🔧 Service Configuration

### 1. Backend Service Configuration
Create systemd service for backend:

```bash
sudo nano /etc/systemd/system/perspectiveupsc-backend.service
```

**Backend Service Configuration:**
```ini
[Unit]
Description=PerspectiveUPSC Backend API
After=network.target mongod.service
Requires=mongod.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/perspectiveupsc/backend
Environment=PATH=/var/www/perspectiveupsc/backend/venv/bin
ExecStart=/var/www/perspectiveupsc/backend/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 2. Frontend Service Configuration (Optional - if not using Nginx static)
```bash
sudo nano /etc/systemd/system/perspectiveupsc-frontend.service
```

**Frontend Service Configuration:**
```ini
[Unit]
Description=PerspectiveUPSC Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/perspectiveupsc/frontend
ExecStart=/usr/bin/yarn start
Environment=NODE_ENV=production
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 3. Enable Services
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable and start backend service
sudo systemctl enable perspectiveupsc-backend
sudo systemctl start perspectiveupsc-backend

# Check status
sudo systemctl status perspectiveupsc-backend
```

---

## 🚀 Application Startup

### 1. Start Backend
```bash
cd /var/www/perspectiveupsc/backend
source venv/bin/activate

# Start with uvicorn
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Or start with systemd service
sudo systemctl start perspectiveupsc-backend
```

### 2. Serve Frontend with Nginx
Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/perspectiveupsc
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name perspectiveupsc.com www.perspectiveupsc.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name perspectiveupsc.com www.perspectiveupsc.com;
    
    # SSL Configuration (add your SSL certificates)
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # Frontend static files
    location / {
        root /var/www/perspectiveupsc/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Add security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
    
    # Backend API proxy
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/perspectiveupsc /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## 🌐 Domain Configuration

### 1. SSL Certificate Setup (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d perspectiveupsc.com -d www.perspectiveupsc.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

### 2. DNS Configuration
Set up A records with your domain provider:

```
Type: A Record
Name: @ (root domain)
Value: YOUR_SERVER_IP
TTL: 300

Type: A Record  
Name: www
Value: YOUR_SERVER_IP
TTL: 300
```

---

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Backend Not Starting
```bash
# Check service logs
sudo journalctl -u perspectiveupsc-backend -f

# Check if port is in use
sudo netstat -tlnp | grep 8001

# Restart service
sudo systemctl restart perspectiveupsc-backend
```

#### 2. Database Connection Issues
```bash
# Check MongoDB status
sudo systemctl status mongod

# Check MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log

# Restart MongoDB
sudo systemctl restart mongod
```

#### 3. Nginx Issues
```bash
# Check Nginx status
sudo systemctl status nginx

# Check configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

#### 4. Frontend Build Issues
```bash
cd /var/www/perspectiveupsc/frontend

# Clear cache and rebuild
rm -rf node_modules package-lock.json
yarn install
yarn build
```

#### 5. Email Issues
```bash
# Test SMTP connectivity
telnet smtpout.secureserver.net 587

# Check backend logs for email errors
sudo journalctl -u perspectiveupsc-backend | grep -i email
```

---

## 🔄 Updates & Maintenance

### 1. Deploying Code Updates
```bash
# Navigate to project directory
cd /var/www/perspectiveupsc

# Pull latest changes from GitHub
git pull origin main

# Update backend dependencies (if requirements.txt changed)
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Restart backend service
sudo systemctl restart perspectiveupsc-backend

# Update frontend (if package.json changed)
cd ../frontend
yarn install
yarn build

# Restart Nginx
sudo systemctl restart nginx

# Check services status
sudo systemctl status perspectiveupsc-backend nginx
```

### 2. Database Backup Script
```bash
# Create backup script
nano /home/backup_mongodb.sh
```

**Backup Script:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/mongodb_backups"
DB_NAME="perspectiveupsc_prod"

mkdir -p $BACKUP_DIR

# Create backup
mongodump --db $DB_NAME --out $BACKUP_DIR/backup_$DATE

# Compress backup
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz -C $BACKUP_DIR backup_$DATE
rm -rf $BACKUP_DIR/backup_$DATE

# Keep only last 7 backups
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.tar.gz"
```

Make executable and add to cron:
```bash
chmod +x /home/backup_mongodb.sh

# Add to crontab (daily backup at 2 AM)
crontab -e
# Add line: 0 2 * * * /home/backup_mongodb.sh
```

### 3. Log Rotation
```bash
# Configure logrotate for application logs
sudo nano /etc/logrotate.d/perspectiveupsc
```

```
/var/log/perspectiveupsc/*.log {
    daily
    missingok
    rotate 14
    compress
    notifempty
    create 0644 www-data www-data
    postrotate
        systemctl reload perspectiveupsc-backend
    endscript
}
```

### 4. Monitoring Setup
```bash
# Install htop for system monitoring
sudo apt install htop

# Monitor services
sudo systemctl status perspectiveupsc-backend nginx mongod

# Monitor logs in real-time
sudo journalctl -f -u perspectiveupsc-backend
```

---

## 📞 Support & Maintenance Checklist

### Daily Tasks
- [ ] Check application accessibility
- [ ] Monitor server resources (CPU, RAM, Disk)
- [ ] Check service status

### Weekly Tasks  
- [ ] Review application logs
- [ ] Check database backup success
- [ ] Update system packages
- [ ] Monitor SSL certificate expiry

### Monthly Tasks
- [ ] Review security updates
- [ ] Analyze application performance
- [ ] Clean old log files
- [ ] Review database size and optimization

---

## 🎯 Quick Deployment Commands

### Full Deployment from Scratch
```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/perspectiveupsc.git
cd perspectiveupsc

# 2. Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configurations

# 3. Setup frontend
cd ../frontend
yarn install
cp .env.example .env
# Edit .env with your configurations
yarn build

# 4. Start services
cd ../backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 &

# 5. Configure Nginx (follow nginx configuration above)
```

### Quick Update Deployment
```bash
cd /var/www/perspectiveupsc
git pull origin main
cd backend && source venv/bin/activate && pip install -r requirements.txt
sudo systemctl restart perspectiveupsc-backend
cd ../frontend && yarn install && yarn build
sudo systemctl restart nginx
```

---

**📝 Note**: Replace placeholder values (YOUR_USERNAME, YOUR_SERVER_IP, etc.) with your actual values during deployment.

**🔒 Security Reminder**: Always use strong passwords, keep systems updated, and implement proper firewall rules for production deployment.