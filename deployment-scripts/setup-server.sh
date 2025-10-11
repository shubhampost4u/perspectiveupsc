#!/bin/bash
# PerspectiveUPSC - Automated Server Setup Script
# Run this script on your Google Cloud VM after first connection

set -e  # Exit on error

echo "=========================================="
echo "PerspectiveUPSC Server Setup"
echo "=========================================="
echo ""

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Node.js
echo "📦 Installing Node.js 18.x..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Yarn
echo "📦 Installing Yarn..."
sudo npm install -g yarn

# Install Python
echo "📦 Installing Python 3 and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Install MongoDB
echo "📦 Installing MongoDB..."
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
echo "🚀 Starting MongoDB..."
sudo systemctl start mongod
sudo systemctl enable mongod

# Install Nginx
echo "📦 Installing Nginx..."
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Install PM2
echo "📦 Installing PM2..."
sudo npm install -g pm2

# Install Certbot
echo "📦 Installing Certbot for SSL..."
sudo apt install -y certbot python3-certbot-nginx

# Install additional utilities
echo "📦 Installing utilities..."
sudo apt install -y git htop curl wget

echo ""
echo "=========================================="
echo "✅ Server setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Clone your repository: git clone https://github.com/YOUR_USERNAME/perspectiveupsc-platform.git"
echo "2. Follow the deployment guide to configure the application"
echo ""
echo "Installed versions:"
node --version
yarn --version
python3 --version
mongod --version | head -1
nginx -v
pm2 --version
