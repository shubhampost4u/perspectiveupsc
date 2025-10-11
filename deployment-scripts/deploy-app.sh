#!/bin/bash
# PerspectiveUPSC - Application Deployment Script
# Run this script after cloning your repository

set -e  # Exit on error

APP_DIR="/var/www/perspectiveupsc"

echo "=========================================="
echo "PerspectiveUPSC Application Deployment"
echo "=========================================="
echo ""

# Check if running from correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Must run from application root directory"
    echo "Expected directory structure:"
    echo "  - backend/"
    echo "  - frontend/"
    exit 1
fi

# Setup Backend
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: backend/.env file not found!"
    echo "Please create backend/.env with required configuration"
    echo "See backend/.env.example for reference"
fi

cd ..

# Setup Frontend
echo "🔧 Setting up frontend..."
cd frontend

# Install dependencies
yarn install

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: frontend/.env file not found!"
    echo "Please create frontend/.env with required configuration"
    echo "See frontend/.env.example for reference"
fi

# Build production version
echo "🏗️  Building frontend..."
yarn build

cd ..

# Create logs directory
mkdir -p logs

# Create ecosystem config if not exists
if [ ! -f "ecosystem.config.js" ]; then
    echo "📝 Creating PM2 ecosystem configuration..."
    cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'perspectiveupsc-backend',
      script: 'venv/bin/uvicorn',
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
EOF
fi

# Start with PM2
echo "🚀 Starting application with PM2..."
pm2 delete perspectiveupsc-backend 2>/dev/null || true
pm2 start ecosystem.config.js
pm2 save

echo ""
echo "=========================================="
echo "✅ Application deployment complete!"
echo "=========================================="
echo ""
echo "Check application status:"
echo "  pm2 status"
echo "  pm2 logs perspectiveupsc-backend"
echo ""
echo "Next steps:"
echo "1. Configure Nginx (see deployment guide)"
echo "2. Setup SSL with Certbot"
echo "3. Configure domain DNS"
echo ""
