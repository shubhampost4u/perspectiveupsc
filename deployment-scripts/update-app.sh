#!/bin/bash
# PerspectiveUPSC - Quick Update Script
# Run this script to deploy updates from GitHub

set -e  # Exit on error

echo "=========================================="
echo "PerspectiveUPSC - Deploying Updates"
echo "=========================================="
echo ""

# Check if running from correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Must run from application root directory"
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Update backend
echo "🔧 Updating backend..."
cd backend
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Update frontend
echo "🔧 Updating frontend..."
cd frontend
yarn install
yarn build
cd ..

# Restart backend
echo "🔄 Restarting backend..."
pm2 restart perspectiveupsc-backend

# Reload Nginx
echo "🔄 Reloading Nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "=========================================="
echo "✅ Update deployment complete!"
echo "=========================================="
echo ""
echo "Check status:"
echo "  pm2 status"
echo "  pm2 logs perspectiveupsc-backend"
echo ""
