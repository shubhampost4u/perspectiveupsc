# PerspectiveUPSC - Quick Deployment Checklist

## 🚀 Pre-Deployment Checklist

### ✅ Server Requirements
- [ ] Ubuntu/CentOS server with 2GB+ RAM
- [ ] Domain name (perspectiveupsc.com) pointing to server IP
- [ ] SSH access to server
- [ ] Root/sudo privileges

### ✅ Required Software Installation
- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed  
- [ ] MongoDB 4.4+ installed and running
- [ ] Nginx installed
- [ ] Git installed
- [ ] PM2 installed (optional)

---

## 📥 Deployment Steps

### 1. Code Deployment
```bash
# Clone from GitHub
cd /var/www/
git clone https://github.com/YOUR_USERNAME/perspectiveupsc.git
cd perspectiveupsc
```

### 2. Backend Setup
```bash
cd backend/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file with:
# - MONGO_URL
# - SECRET_KEY  
# - SMTP credentials
# - Razorpay LIVE keys
```

### 3. Frontend Setup  
```bash
cd frontend/
yarn install

# Create .env file with:
# - REACT_APP_BACKEND_URL=https://perspectiveupsc.com

yarn build
```

### 4. Database Setup
```bash
# Create admin user in MongoDB
python3 backend/init_admin.py
```

### 5. Service Configuration
```bash
# Create systemd service files
sudo systemctl enable perspectiveupsc-backend
sudo systemctl start perspectiveupsc-backend
```

### 6. Nginx Configuration
```bash
# Configure reverse proxy
# Enable SSL with Let's Encrypt
sudo certbot --nginx -d perspectiveupsc.com
```

---

## 🔧 Environment Configuration

### Backend .env (Production)
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=perspectiveupsc_prod
SECRET_KEY=your-32-char-secret-key
SMTP_SERVER=smtpout.secureserver.net  
SMTP_PORT=587
SMTP_USERNAME=admin@perspectiveupsc.com
SMTP_PASSWORD=Perspective@2025
RAZORPAY_KEY_ID=rzp_live_YOUR_KEY
RAZORPAY_KEY_SECRET=your_live_secret
```

### Frontend .env (Production)  
```env
REACT_APP_BACKEND_URL=https://perspectiveupsc.com
GENERATE_SOURCEMAP=false
```

---

## ✅ Post-Deployment Verification

### Check Services
- [ ] Backend API responding: `curl https://perspectiveupsc.com/api/`
- [ ] Frontend loading: Visit https://perspectiveupsc.com
- [ ] Database connected: Check MongoDB logs
- [ ] SSL certificate active: Check https://

### Test Core Features
- [ ] User registration working
- [ ] Admin login working (perspectiveupsc1@gmail.com / perspective@2025)
- [ ] Test creation working  
- [ ] Cart functionality working
- [ ] Payment integration working
- [ ] Password reset emails sending

### Monitor Resources
- [ ] Check CPU/RAM usage: `htop`
- [ ] Check disk space: `df -h`
- [ ] Check service status: `systemctl status perspectiveupsc-backend nginx`

---

## 🔄 Update Deployment Process

### For Code Changes
```bash
cd /var/www/perspectiveupsc
git pull origin main

# If backend changes:
cd backend && source venv/bin/activate
pip install -r requirements.txt  
sudo systemctl restart perspectiveupsc-backend

# If frontend changes:
cd frontend && yarn install && yarn build
sudo systemctl restart nginx
```

### For Environment Changes
```bash
# Edit .env files
nano backend/.env
nano frontend/.env

# Rebuild frontend if needed
cd frontend && yarn build

# Restart services
sudo systemctl restart perspectiveupsc-backend nginx
```

---

## 🆘 Emergency Troubleshooting

### Backend Not Responding
```bash
sudo systemctl status perspectiveupsc-backend
sudo journalctl -u perspectiveupsc-backend -f
sudo systemctl restart perspectiveupsc-backend
```

### Frontend Not Loading
```bash
sudo systemctl status nginx
sudo nginx -t
sudo systemctl restart nginx
```

### Database Issues
```bash
sudo systemctl status mongod
sudo systemctl restart mongod
```

### SSL Certificate Issues
```bash
sudo certbot certificates
sudo certbot renew
```

---

## 📱 Quick Commands Reference

### Service Management
```bash
# Check all services
sudo systemctl status perspectiveupsc-backend nginx mongod

# Restart all services  
sudo systemctl restart perspectiveupsc-backend nginx

# Check logs
sudo journalctl -f -u perspectiveupsc-backend
```

### Application Management
```bash
# Update from GitHub
cd /var/www/perspectiveupsc && git pull

# Full rebuild
cd frontend && yarn build && cd ../backend && sudo systemctl restart perspectiveupsc-backend
```

### Monitoring
```bash
# System resources
htop
df -h

# Application logs
tail -f /var/log/nginx/access.log
sudo journalctl -u perspectiveupsc-backend -f
```

---

## 📞 Support Information

### Default Credentials
- **Admin**: perspectiveupsc1@gmail.com / perspective@2025
- **Database**: perspectiveupsc_prod
- **Domain**: https://perspectiveupsc.com

### Important Files
- **Backend Config**: `/var/www/perspectiveupsc/backend/.env`
- **Frontend Config**: `/var/www/perspectiveupsc/frontend/.env`  
- **Nginx Config**: `/etc/nginx/sites-available/perspectiveupsc`
- **Service Config**: `/etc/systemd/system/perspectiveupsc-backend.service`

### Key Ports
- **Backend API**: 8001
- **Frontend**: 3000 (dev) / 80,443 (production via Nginx)
- **MongoDB**: 27017
- **SSH**: 22

---

**🎯 Remember**: Always test in a staging environment before deploying to production!