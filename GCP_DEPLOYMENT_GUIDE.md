# 🚀 Complete Deployment Guide: PerspectiveUPSC on Google Cloud VM

## 📋 Prerequisites
- Google Cloud Platform account
- Domain name (perspectiveupsc.com) with DNS access
- GitHub account
- Local git installed

---

## Part 1: Push Code to GitHub

### Step 1.1: Create GitHub Repository
1. Go to https://github.com and log in
2. Click **"New repository"** or **"+"** → **"New repository"**
3. Repository name: `perspectiveupsc-platform`
4. Make it **Private** (recommended for production code)
5. **Do NOT** initialize with README (we already have code)
6. Click **"Create repository"**

### Step 1.2: Prepare Code for GitHub
```bash
# Navigate to your app directory
cd /app

# Initialize git if not already done
git init

# Create .gitignore file
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/

# Environment variables
.env
.env.local
.env.production
backend/.env
frontend/.env

# Build files
frontend/build/
frontend/.next/
dist/

# Logs
*.log
/var/log/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Test files
test_*.py
*_test.py
backend_test*.py

# Emergent specific
.emergent/
EOF

# Add all files
git add .

# Commit
git commit -m "Initial commit: PerspectiveUPSC platform production ready"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/perspectiveupsc-platform.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 1.3: Add Environment Template
```bash
# Create .env.example for documentation
cat > backend/.env.example << 'EOF'
# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017/perspectiveupsc

# JWT Secret
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# SMTP Email Configuration (GoDaddy)
SMTP_SERVER=smtpout.secureserver.net
SMTP_PORT=587
SMTP_USERNAME=admin@perspectiveupsc.com
SMTP_PASSWORD=your-email-password
SMTP_FROM_EMAIL=admin@perspectiveupsc.com
SMTP_FROM_NAME=PerspectiveUPSC

# Razorpay Configuration
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-secret

# Application Settings
FRONTEND_URL=https://www.perspectiveupsc.com
EOF

cat > frontend/.env.example << 'EOF'
REACT_APP_BACKEND_URL=https://www.perspectiveupsc.com/api
EOF

git add backend/.env.example frontend/.env.example
git commit -m "Add environment variable templates"
git push
```

---

## Part 2: Create Google Cloud VM

### Step 2.1: Create VM Instance
1. Go to **Google Cloud Console**: https://console.cloud.google.com
2. Navigate to **Compute Engine** → **VM instances**
3. Click **"CREATE INSTANCE"**

**VM Configuration:**
```
Name: perspectiveupsc-server
Region: asia-south1 (Mumbai) or your preferred region
Zone: asia-south1-a

Machine configuration:
  Series: E2
  Machine type: e2-medium (2 vCPU, 4 GB memory)
  
Boot disk:
  Click "CHANGE"
  Operating system: Ubuntu
  Version: Ubuntu 22.04 LTS
  Boot disk type: Balanced persistent disk
  Size: 30 GB

Firewall:
  ☑ Allow HTTP traffic
  ☑ Allow HTTPS traffic
```

4. Click **"CREATE"**
5. Wait for VM to be created (~1-2 minutes)

### Step 2.2: Configure Firewall Rules
1. Go to **VPC network** → **Firewall**
2. Click **"CREATE FIREWALL RULE"**

**Backend Port Rule:**
```
Name: allow-backend-8001
Targets: All instances in the network
Source IP ranges: 0.0.0.0/0
Protocols and ports: tcp:8001
```

**Frontend Port Rule:**
```
Name: allow-frontend-3000
Targets: All instances in the network
Source IP ranges: 0.0.0.0/0
Protocols and ports: tcp:3000
```

### Step 2.3: Reserve Static IP Address
1. Go to **VPC network** → **IP addresses** → **External IP addresses**
2. Find your VM's IP → Change **Type** from **Ephemeral** to **Static**
3. Give it a name: `perspectiveupsc-ip`
4. Click **"RESERVE"**
5. **Note down this IP address** - you'll need it for DNS configuration

---

## Part 3: Connect to VM and Install Dependencies

### Step 3.1: Connect to VM
```bash
# From Google Cloud Console, click "SSH" button next to your VM
# Or use gcloud CLI:
gcloud compute ssh perspectiveupsc-server --zone=asia-south1-a
```

### Step 3.2: Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Step 3.3: Install Node.js and Yarn
```bash
# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Yarn
sudo npm install -g yarn

# Verify installations
node --version  # Should show v18.x.x
yarn --version
```

### Step 3.4: Install Python and Pip
```bash
# Install Python 3.11
sudo apt install -y python3 python3-pip python3-venv

# Verify
python3 --version
pip3 --version
```

### Step 3.5: Install MongoDB
```bash
# Import MongoDB public GPG key
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# Create list file for MongoDB
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Install MongoDB
sudo apt update
sudo apt install -y mongodb-org

# Start and enable MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify
sudo systemctl status mongod
```

### Step 3.6: Install Nginx
```bash
sudo apt install -y nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify
sudo systemctl status nginx
```

### Step 3.7: Install PM2 (Process Manager)
```bash
sudo npm install -g pm2
```

### Step 3.8: Install Certbot (for SSL)
```bash
sudo apt install -y certbot python3-certbot-nginx
```

---

## Part 4: Clone and Setup Application

### Step 4.1: Clone Repository
```bash
# Create application directory
sudo mkdir -p /var/www
cd /var/www

# Clone your repository (replace with your actual GitHub URL)
sudo git clone https://github.com/YOUR_USERNAME/perspectiveupsc-platform.git perspectiveupsc

# Change ownership to current user
sudo chown -R $USER:$USER /var/www/perspectiveupsc

# Navigate to app directory
cd /var/www/perspectiveupsc
```

### Step 4.2: Setup Backend
```bash
# Navigate to backend
cd /var/www/perspectiveupsc/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
```

**Add the following to backend/.env:**
```bash
MONGO_URL=mongodb://localhost:27017/perspectiveupsc
JWT_SECRET=CHANGE-THIS-TO-A-SECURE-RANDOM-STRING-IN-PRODUCTION
SMTP_SERVER=smtpout.secureserver.net
SMTP_PORT=587
SMTP_USERNAME=admin@perspectiveupsc.com
SMTP_PASSWORD=YOUR-EMAIL-PASSWORD
SMTP_FROM_EMAIL=admin@perspectiveupsc.com
SMTP_FROM_NAME=PerspectiveUPSC
RAZORPAY_KEY_ID=YOUR-RAZORPAY-KEY
RAZORPAY_KEY_SECRET=YOUR-RAZORPAY-SECRET
FRONTEND_URL=https://www.perspectiveupsc.com
```

**Save and exit (Ctrl+X, then Y, then Enter)**

### Step 4.3: Setup Frontend
```bash
# Navigate to frontend
cd /var/www/perspectiveupsc/frontend

# Install dependencies
yarn install

# Create .env file
nano .env
```

**Add the following to frontend/.env:**
```bash
REACT_APP_BACKEND_URL=https://www.perspectiveupsc.com/api
```

**Save and exit**

```bash
# Build production version
yarn build
```

---

## Part 5: Configure Nginx Reverse Proxy

### Step 5.1: Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/perspectiveupsc
```

**Add the following configuration:**
```nginx
server {
    listen 80;
    server_name perspectiveupsc.com www.perspectiveupsc.com;

    # Frontend - Serve React build
    location / {
        root /var/www/perspectiveupsc/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API - Proxy to FastAPI
    location /api/ {
        proxy_pass http://localhost:8001/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Increase timeout for long-running requests
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
    }

    # Client max body size for file uploads
    client_max_body_size 10M;
}
```

**Save and exit**

### Step 5.2: Enable Configuration
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/perspectiveupsc /etc/nginx/sites-enabled/

# Remove default configuration
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## Part 6: Setup PM2 Process Management

### Step 6.1: Create PM2 Ecosystem File
```bash
cd /var/www/perspectiveupsc
nano ecosystem.config.js
```

**Add the following:**
```javascript
module.exports = {
  apps: [
    {
      name: 'perspectiveupsc-backend',
      script: '/var/www/perspectiveupsc/backend/venv/bin/uvicorn',
      args: 'server:app --host 0.0.0.0 --port 8001',
      cwd: '/var/www/perspectiveupsc/backend',
      interpreter: 'none',
      env: {
        PYTHONPATH: '/var/www/perspectiveupsc/backend'
      },
      error_file: '/var/www/perspectiveupsc/logs/backend-error.log',
      out_file: '/var/www/perspectiveupsc/logs/backend-out.log',
      time: true,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G'
    }
  ]
};
```

**Save and exit**

### Step 6.2: Create Logs Directory
```bash
mkdir -p /var/www/perspectiveupsc/logs
```

### Step 6.3: Start Application with PM2
```bash
cd /var/www/perspectiveupsc

# Start the application
pm2 start ecosystem.config.js

# Save PM2 process list
pm2 save

# Setup PM2 to start on system boot
pm2 startup
# Follow the command it gives you (will be something like: sudo env PATH=...)

# Check status
pm2 status
pm2 logs
```

---

## Part 7: Configure Domain DNS

### Step 7.1: Add DNS Records
Go to your domain registrar (GoDaddy, Namecheap, Cloudflare, etc.) and add these records:

**A Records:**
```
Type: A
Host: @
Value: YOUR-GCP-VM-STATIC-IP
TTL: 300 (or default)

Type: A
Host: www
Value: YOUR-GCP-VM-STATIC-IP
TTL: 300 (or default)
```

**Example with IP 34.131.45.67:**
```
@ → 34.131.45.67
www → 34.131.45.67
```

### Step 7.2: Wait for DNS Propagation
```bash
# Check DNS propagation (5-15 minutes, up to 48 hours)
nslookup perspectiveupsc.com
nslookup www.perspectiveupsc.com

# Or use online tool: https://dnschecker.org/
```

---

## Part 8: Setup SSL Certificate (HTTPS)

### Step 8.1: Obtain SSL Certificate
```bash
# Make sure DNS is propagated first!
# Replace email with your actual email

sudo certbot --nginx -d perspectiveupsc.com -d www.perspectiveupsc.com --email admin@perspectiveupsc.com --agree-tos --no-eff-email
```

**Follow the prompts:**
- Enter email address
- Agree to terms
- Choose to redirect HTTP to HTTPS (option 2)

### Step 8.2: Verify SSL
```bash
# Check certificate status
sudo certbot certificates

# Test auto-renewal
sudo certbot renew --dry-run
```

### Step 8.3: Setup Auto-Renewal
```bash
# Certbot auto-renewal is already configured, verify with:
sudo systemctl status certbot.timer
```

---

## Part 9: Verify Deployment

### Step 9.1: Check Services
```bash
# Check MongoDB
sudo systemctl status mongod

# Check Nginx
sudo systemctl status nginx

# Check PM2 processes
pm2 status
pm2 logs

# Check if backend is responding
curl http://localhost:8001/api/health || echo "Check backend logs"

# Check Nginx access
curl http://localhost
```

### Step 9.2: Test Application
1. Open browser: https://www.perspectiveupsc.com
2. Test student registration
3. Test admin login: perspectiveupsc1@gmail.com / perspective@2025
4. Test all features:
   - ✅ Student registration/login
   - ✅ Test cart and checkout
   - ✅ Password reset
   - ✅ Admin dashboard
   - ✅ Bulk upload
   - ✅ Test creation

---

## Part 10: Post-Deployment Configuration

### Step 10.1: Switch Razorpay to Live Mode
```bash
# Edit backend .env
nano /var/www/perspectiveupsc/backend/.env

# Update these lines with LIVE keys:
RAZORPAY_KEY_ID=rzp_live_XXXXXXXXXX
RAZORPAY_KEY_SECRET=LIVE_SECRET_KEY

# Restart backend
pm2 restart perspectiveupsc-backend
```

### Step 10.2: Configure MongoDB Security (Recommended)
```bash
# Create MongoDB admin user
mongosh

use admin
db.createUser({
  user: "admin",
  pwd: "STRONG-PASSWORD-HERE",
  roles: ["userAdminAnyDatabase", "readWriteAnyDatabase"]
})

# Exit mongosh
exit

# Enable authentication
sudo nano /etc/mongod.conf

# Add under security:
security:
  authorization: enabled

# Restart MongoDB
sudo systemctl restart mongod

# Update backend .env with authentication:
MONGO_URL=mongodb://admin:STRONG-PASSWORD-HERE@localhost:27017/perspectiveupsc?authSource=admin
```

### Step 10.3: Setup Backup Script
```bash
# Create backup directory
mkdir -p /var/backups/perspectiveupsc

# Create backup script
nano /var/www/perspectiveupsc/backup.sh
```

**Add this content:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/perspectiveupsc"

# Backup MongoDB
mongodump --db=perspectiveupsc --out=$BACKUP_DIR/mongo_$DATE

# Keep only last 7 days of backups
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;

echo "Backup completed: $DATE"
```

**Make executable and setup cron:**
```bash
chmod +x /var/www/perspectiveupsc/backup.sh

# Setup daily backup at 2 AM
crontab -e

# Add this line:
0 2 * * * /var/www/perspectiveupsc/backup.sh >> /var/www/perspectiveupsc/logs/backup.log 2>&1
```

---

## Part 11: Monitoring and Maintenance

### Step 11.1: Useful Commands
```bash
# View PM2 logs
pm2 logs perspectiveupsc-backend
pm2 logs --lines 100

# Monitor PM2 processes
pm2 monit

# Restart application
pm2 restart perspectiveupsc-backend

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check system resources
htop  # Install with: sudo apt install htop

# Check disk space
df -h

# Check MongoDB status
sudo systemctl status mongod
mongosh --eval "db.stats()"
```

### Step 11.2: Deploy Updates
```bash
# SSH to server
cd /var/www/perspectiveupsc

# Pull latest changes
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Update frontend
cd frontend
yarn install
yarn build
cd ..

# Restart backend
pm2 restart perspectiveupsc-backend

# Reload Nginx (if config changed)
sudo nginx -t && sudo systemctl reload nginx
```

---

## 🔒 Security Checklist

- [ ] Change default JWT_SECRET in .env
- [ ] Enable MongoDB authentication
- [ ] Configure firewall (UFW) on VM
- [ ] Setup automated backups
- [ ] Enable Fail2Ban for SSH protection
- [ ] Keep system updated: `sudo apt update && sudo apt upgrade`
- [ ] Monitor logs regularly
- [ ] Use strong passwords for all services
- [ ] Setup monitoring alerts (Google Cloud Monitoring)

---

## 📊 Cost Estimation (Google Cloud)

**Monthly costs:**
- VM Instance (e2-medium): ~$25-30/month
- Static IP: $2.50/month (free while attached to running VM)
- Storage (30GB): ~$1/month
- Bandwidth: ~$0.08-0.12/GB

**Total estimated: $25-35/month**

---

## 🆘 Troubleshooting

### Backend not starting:
```bash
pm2 logs perspectiveupsc-backend
# Check for Python errors or missing dependencies
```

### Frontend not loading:
```bash
sudo nginx -t  # Test Nginx config
sudo tail -f /var/log/nginx/error.log
```

### MongoDB connection issues:
```bash
sudo systemctl status mongod
mongosh  # Try connecting
```

### SSL certificate issues:
```bash
sudo certbot certificates
sudo certbot renew --dry-run
```

---

## ✅ Deployment Complete!

Your PerspectiveUPSC platform should now be live at:
- 🌐 **https://www.perspectiveupsc.com**
- 🔒 **SSL enabled**
- 🚀 **Production ready**

**Admin Access:**
- Email: perspectiveupsc1@gmail.com
- Password: perspective@2025

---

## 📞 Need Help?

If you encounter issues:
1. Check PM2 logs: `pm2 logs`
2. Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Check MongoDB: `sudo systemctl status mongod`
4. Verify DNS propagation: https://dnschecker.org/

**Happy deploying! 🎉**
