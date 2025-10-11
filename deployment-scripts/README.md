# 🚀 Deployment Scripts for PerspectiveUPSC

This directory contains automated scripts to simplify the deployment process on Google Cloud VM.

---

## 📁 Available Scripts

### 1. `setup-server.sh`
**Purpose:** Initial server setup - installs all required dependencies
**When to use:** First time setting up your Google Cloud VM
**What it does:**
- Updates system packages
- Installs Node.js 18.x and Yarn
- Installs Python 3 and pip
- Installs MongoDB 7.0
- Installs Nginx
- Installs PM2 process manager
- Installs Certbot for SSL

**Usage:**
```bash
# On your Google Cloud VM
wget https://raw.githubusercontent.com/YOUR_USERNAME/perspectiveupsc-platform/main/deployment-scripts/setup-server.sh
chmod +x setup-server.sh
./setup-server.sh
```

**Time:** ~10-15 minutes

---

### 2. `deploy-app.sh`
**Purpose:** Deploy the PerspectiveUPSC application
**When to use:** After cloning your repository and setting up .env files
**What it does:**
- Sets up Python virtual environment
- Installs backend dependencies
- Installs frontend dependencies
- Builds production frontend
- Creates PM2 ecosystem configuration
- Starts application with PM2

**Usage:**
```bash
# After cloning your repository
cd /var/www/perspectiveupsc
./deployment-scripts/deploy-app.sh
```

**Prerequisites:**
- Server dependencies installed (run setup-server.sh first)
- Repository cloned
- backend/.env file configured
- frontend/.env file configured

**Time:** ~5-10 minutes

---

### 3. `update-app.sh`
**Purpose:** Deploy updates from GitHub
**When to use:** When you push new code to GitHub and want to update production
**What it does:**
- Pulls latest changes from GitHub
- Updates backend dependencies
- Rebuilds frontend
- Restarts backend service
- Reloads Nginx

**Usage:**
```bash
cd /var/www/perspectiveupsc
./deployment-scripts/update-app.sh
```

**Time:** ~3-5 minutes

---

## 🔄 Typical Workflow

### Initial Deployment:
```bash
# 1. Connect to your VM
gcloud compute ssh perspectiveupsc-server

# 2. Setup server dependencies
wget https://raw.githubusercontent.com/YOUR_USERNAME/perspectiveupsc-platform/main/deployment-scripts/setup-server.sh
chmod +x setup-server.sh
./setup-server.sh

# 3. Clone repository
sudo mkdir -p /var/www
cd /var/www
sudo git clone https://github.com/YOUR_USERNAME/perspectiveupsc-platform.git perspectiveupsc
sudo chown -R $USER:$USER perspectiveupsc

# 4. Configure environment variables
cd perspectiveupsc
nano backend/.env    # Add your configuration
nano frontend/.env   # Add your configuration

# 5. Deploy application
./deployment-scripts/deploy-app.sh

# 6. Configure Nginx (manual step - see main guide)
# 7. Setup SSL with Certbot (manual step - see main guide)
```

### Deploying Updates:
```bash
# Connect to VM
gcloud compute ssh perspectiveupsc-server

# Navigate to app directory
cd /var/www/perspectiveupsc

# Deploy updates
./deployment-scripts/update-app.sh

# Check status
pm2 status
pm2 logs
```

---

## ⚙️ Manual Steps Required

These scripts automate most of the deployment process, but you'll still need to:

1. **Create and configure .env files** (backend/.env and frontend/.env)
2. **Configure Nginx** (create /etc/nginx/sites-available/perspectiveupsc)
3. **Setup DNS records** (point your domain to VM IP)
4. **Obtain SSL certificate** (run certbot command)
5. **Configure MongoDB authentication** (optional but recommended)

See the full deployment guide (`GCP_DEPLOYMENT_GUIDE.md`) for detailed instructions on these steps.

---

## 🔍 Verification Commands

After running the scripts, verify everything is working:

```bash
# Check installed versions
node --version
yarn --version
python3 --version
mongod --version
nginx -v
pm2 --version

# Check running services
sudo systemctl status mongod
sudo systemctl status nginx
pm2 status

# View application logs
pm2 logs perspectiveupsc-backend

# Check if backend is responding
curl http://localhost:8001/api/health || echo "Backend may not have /health endpoint"

# Monitor processes
pm2 monit
```

---

## 🆘 Troubleshooting

### Script fails with "Permission denied"
```bash
chmod +x deployment-scripts/*.sh
```

### "git: command not found"
```bash
sudo apt install git
```

### Backend fails to start
```bash
# Check logs
pm2 logs perspectiveupsc-backend

# Manually test backend
cd /var/www/perspectiveupsc/backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001
```

### Frontend build fails
```bash
# Check for errors
cd /var/www/perspectiveupsc/frontend
yarn build

# Check Node.js version (should be 18.x)
node --version
```

---

## 📝 Notes

- These scripts assume you're using Ubuntu 22.04 LTS
- Scripts use `sudo` where necessary and will prompt for password
- All scripts have error checking (`set -e`) and will stop if something fails
- Logs are stored in `/var/www/perspectiveupsc/logs/`
- PM2 automatically restarts your application if it crashes

---

## 🔗 Related Documentation

- **Full Deployment Guide:** `/app/GCP_DEPLOYMENT_GUIDE.md`
- **Quick Checklist:** `/app/QUICK_DEPLOYMENT_CHECKLIST.md`
- **Application Documentation:** `/app/README.md`

---

## 💡 Tips

1. **Always test in preview mode** before deploying to production
2. **Backup your .env files** - they contain sensitive credentials
3. **Use version control** - commit your changes before deploying updates
4. **Monitor logs regularly** - `pm2 logs` is your friend
5. **Setup automated backups** - see deployment guide Section 10.3

---

**Happy deploying! 🎉**
