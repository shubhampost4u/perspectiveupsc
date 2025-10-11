# ✅ Quick Deployment Checklist

Use this checklist to track your deployment progress.

---

## Phase 1: GitHub Setup ⏱️ 10 minutes

- [ ] **1.1** Create GitHub repository (private recommended)
- [ ] **1.2** Add code to repository
  ```bash
  cd /app
  git remote add origin https://github.com/YOUR_USERNAME/perspectiveupsc-platform.git
  git push -u origin main
  ```
- [ ] **1.3** Verify repository is accessible
- [ ] **1.4** Create .env.example files (already created in guide)

**📝 Note:** Keep your GitHub URL handy for VM setup

---

## Phase 2: Google Cloud VM Setup ⏱️ 15 minutes

- [ ] **2.1** Go to Google Cloud Console → Compute Engine
- [ ] **2.2** Create VM instance
  - Name: `perspectiveupsc-server`
  - Region: `asia-south1` (Mumbai) or preferred
  - Machine type: `e2-medium` (2 vCPU, 4GB RAM)
  - Boot disk: Ubuntu 22.04 LTS, 30GB
  - Firewall: ✅ HTTP, ✅ HTTPS
- [ ] **2.3** Create firewall rules
  - Rule 1: `allow-backend-8001` → TCP:8001
  - Rule 2: `allow-frontend-3000` → TCP:3000
- [ ] **2.4** Reserve static IP address
  - VPC Network → IP Addresses → Make Static
  - Name: `perspectiveupsc-ip`
  - **Write down IP:** _________________

---

## Phase 3: Server Configuration ⏱️ 20 minutes

- [ ] **3.1** Connect to VM via SSH
- [ ] **3.2** Download setup script
  ```bash
  wget https://raw.githubusercontent.com/YOUR_USERNAME/perspectiveupsc-platform/main/deployment-scripts/setup-server.sh
  chmod +x setup-server.sh
  ./setup-server.sh
  ```
  
  **OR manually follow these steps:**
  
- [ ] **3.3** Update system: `sudo apt update && sudo apt upgrade -y`
- [ ] **3.4** Install Node.js 18.x and Yarn
- [ ] **3.5** Install Python 3 and pip
- [ ] **3.6** Install MongoDB 7.0
- [ ] **3.7** Install Nginx
- [ ] **3.8** Install PM2
- [ ] **3.9** Install Certbot (for SSL)

**✅ Verify installations:**
```bash
node --version    # Should be v18.x.x
yarn --version
python3 --version
mongod --version
nginx -v
pm2 --version
```

---

## Phase 4: Application Deployment ⏱️ 15 minutes

- [ ] **4.1** Clone repository
  ```bash
  sudo mkdir -p /var/www
  cd /var/www
  sudo git clone https://github.com/YOUR_USERNAME/perspectiveupsc-platform.git perspectiveupsc
  sudo chown -R $USER:$USER /var/www/perspectiveupsc
  cd /var/www/perspectiveupsc
  ```

- [ ] **4.2** Create backend/.env file
  ```bash
  nano backend/.env
  ```
  **Required variables:**
  ```bash
  MONGO_URL=mongodb://localhost:27017/perspectiveupsc
  JWT_SECRET=CHANGE-THIS-TO-A-SECURE-RANDOM-STRING
  SMTP_SERVER=smtpout.secureserver.net
  SMTP_PORT=587
  SMTP_USERNAME=admin@perspectiveupsc.com
  SMTP_PASSWORD=your-godaddy-email-password
  SMTP_FROM_EMAIL=admin@perspectiveupsc.com
  SMTP_FROM_NAME=PerspectiveUPSC
  RAZORPAY_KEY_ID=your-razorpay-key-id
  RAZORPAY_KEY_SECRET=your-razorpay-secret
  FRONTEND_URL=https://www.perspectiveupsc.com
  ```

- [ ] **4.3** Create frontend/.env file
  ```bash
  nano frontend/.env
  ```
  ```bash
  REACT_APP_BACKEND_URL=https://www.perspectiveupsc.com/api
  ```

- [ ] **4.4** Setup backend
  ```bash
  cd /var/www/perspectiveupsc/backend
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

- [ ] **4.5** Build frontend
  ```bash
  cd /var/www/perspectiveupsc/frontend
  yarn install
  yarn build
  ```

- [ ] **4.6** Start application with PM2
  ```bash
  cd /var/www/perspectiveupsc
  pm2 start ecosystem.config.js
  pm2 save
  pm2 startup  # Run the command it outputs
  ```

---

## Phase 5: Nginx Configuration ⏱️ 10 minutes

- [ ] **5.1** Create Nginx config
  ```bash
  sudo nano /etc/nginx/sites-available/perspectiveupsc
  ```
  **Copy configuration from deployment guide**

- [ ] **5.2** Enable site
  ```bash
  sudo ln -s /etc/nginx/sites-available/perspectiveupsc /etc/nginx/sites-enabled/
  sudo rm /etc/nginx/sites-enabled/default
  ```

- [ ] **5.3** Test and reload
  ```bash
  sudo nginx -t
  sudo systemctl reload nginx
  ```

---

## Phase 6: DNS Configuration ⏱️ 5 minutes (+ propagation time)

- [ ] **6.1** Go to your domain registrar (GoDaddy/Namecheap/etc.)
- [ ] **6.2** Add A record: `@` → Your VM Static IP
- [ ] **6.3** Add A record: `www` → Your VM Static IP
- [ ] **6.4** Wait for DNS propagation (5-60 minutes)
- [ ] **6.5** Verify DNS
  ```bash
  nslookup perspectiveupsc.com
  nslookup www.perspectiveupsc.com
  ```

**Check online:** https://dnschecker.org/

---

## Phase 7: SSL Certificate ⏱️ 5 minutes

⚠️ **IMPORTANT: Only proceed after DNS is propagated!**

- [ ] **7.1** Obtain SSL certificate
  ```bash
  sudo certbot --nginx -d perspectiveupsc.com -d www.perspectiveupsc.com \
    --email admin@perspectiveupsc.com --agree-tos --no-eff-email
  ```

- [ ] **7.2** Choose option 2 (redirect HTTP to HTTPS)

- [ ] **7.3** Verify SSL
  ```bash
  sudo certbot certificates
  ```

- [ ] **7.4** Test auto-renewal
  ```bash
  sudo certbot renew --dry-run
  ```

---

## Phase 8: Final Verification ⏱️ 10 minutes

- [ ] **8.1** Check all services
  ```bash
  sudo systemctl status mongod
  sudo systemctl status nginx
  pm2 status
  pm2 logs
  ```

- [ ] **8.2** Test in browser: https://www.perspectiveupsc.com

- [ ] **8.3** Test all features:
  - [ ] Homepage loads
  - [ ] Student registration
  - [ ] Student login
  - [ ] Admin login (perspectiveupsc1@gmail.com / perspective@2025)
  - [ ] Test cart functionality
  - [ ] Password reset
  - [ ] Bulk upload
  - [ ] Create test
  - [ ] Payment flow

---

## Phase 9: Production Configuration ⏱️ 10 minutes

- [ ] **9.1** Switch Razorpay to live mode
  ```bash
  nano /var/www/perspectiveupsc/backend/.env
  # Update RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET with live keys
  pm2 restart perspectiveupsc-backend
  ```

- [ ] **9.2** Configure MongoDB authentication (optional but recommended)
  - See deployment guide Section 10.2

- [ ] **9.3** Setup automated backups
  - See deployment guide Section 10.3

- [ ] **9.4** Configure monitoring
  - Setup Google Cloud Monitoring alerts
  - Configure PM2 monitoring: `pm2 install pm2-logrotate`

---

## Phase 10: Security Hardening ⏱️ 15 minutes

- [ ] **10.1** Change JWT_SECRET to a strong random string
- [ ] **10.2** Enable MongoDB authentication
- [ ] **10.3** Configure UFW firewall
  ```bash
  sudo ufw allow 22/tcp    # SSH
  sudo ufw allow 80/tcp    # HTTP
  sudo ufw allow 443/tcp   # HTTPS
  sudo ufw enable
  ```
- [ ] **10.4** Install Fail2Ban
  ```bash
  sudo apt install fail2ban
  sudo systemctl enable fail2ban
  ```
- [ ] **10.5** Setup log rotation
  ```bash
  pm2 install pm2-logrotate
  ```

---

## 🎉 Deployment Complete!

**Your application is now live at:**
- 🌐 **https://www.perspectiveupsc.com**
- 🔒 **SSL Enabled**
- 🚀 **Production Ready**

---

## 📊 Post-Deployment Tasks

### Daily:
- [ ] Monitor PM2 logs: `pm2 logs`
- [ ] Check system resources: `htop`

### Weekly:
- [ ] Review error logs
- [ ] Check backup status
- [ ] Monitor disk space: `df -h`

### Monthly:
- [ ] Update system: `sudo apt update && sudo apt upgrade`
- [ ] Review security patches
- [ ] Test backup restoration
- [ ] Review SSL certificate expiry

---

## 🆘 Quick Troubleshooting

### Backend not working:
```bash
pm2 logs perspectiveupsc-backend
pm2 restart perspectiveupsc-backend
```

### Frontend not loading:
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### MongoDB issues:
```bash
sudo systemctl status mongod
sudo systemctl restart mongod
```

### SSL certificate issues:
```bash
sudo certbot certificates
sudo certbot renew
```

---

## 📞 Need Help?

Refer to the full deployment guide: `GCP_DEPLOYMENT_GUIDE.md`

---

**Total Estimated Time: 2-3 hours**
*(Excluding DNS propagation time)*
