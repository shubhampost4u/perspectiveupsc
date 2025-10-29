# 🚀 Quick Start Guide - PerspectiveUPSC Platform

**Last Updated:** October 23, 2025  
**Status:** ✅ Production Ready

---

## 📋 What's New in This Version

✨ **Google OAuth Sign-in** - Login with Google account  
✨ **Admin Management** - Easy admin account creation  
✨ **GCP Deployment** - Complete deployment guide + automation  
✨ **Payment Gateway** - Razorpay verified and working  
✨ **Bug Fixes** - Critical authentication issues resolved

---

## ⚡ Quick Commands

### Create Admin Account
```bash
cd /app
python3 create_admin.py

# Or with custom credentials:
python3 create_admin.py your-email@domain.com YourPassword123 "Your Name"
```

**Default Admin:**
- Email: `perspectiveupsc1@gmail.com`
- Password: `perspective@2025`

### Start Development
```bash
# Backend
cd /app/backend
source venv/bin/activate
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Frontend (new terminal)
cd /app/frontend
yarn start
```

### Restart Services (Production)
```bash
sudo supervisorctl restart all
sudo supervisorctl status
```

### Check Logs
```bash
# Backend errors
tail -f /var/log/supervisor/backend.err.log

# Backend output
tail -f /var/log/supervisor/backend.out.log

# All logs
sudo supervisorctl tail -f backend stderr
```

---

## 🔐 Login Credentials

### Admin Account
```
Email: perspectiveupsc1@gmail.com
Password: perspective@2025
Role: Admin
Access: Full admin dashboard, test creation, analytics
```

### Test Student Account
Create via registration or use Google Sign-in

---

## 🌐 Access URLs

### Development
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs

### Production
- **Application:** https://www.perspectiveupsc.com
- **Admin:** https://www.perspectiveupsc.com/admin
- **Student:** https://www.perspectiveupsc.com/dashboard

---

## 🎯 Key Features

### Authentication
✅ Email/Password registration and login  
✅ Google Sign-in (OAuth)  
✅ Password reset with 6-digit OTP  
✅ Session management (7-day expiry)  
✅ JWT token authentication

### Admin Features
✅ Create/edit/delete tests  
✅ Bulk upload questions (Excel - 120 questions)  
✅ View all students and purchases  
✅ Analytics dashboard  
✅ Test activation/deactivation

### Student Features
✅ Browse and purchase tests  
✅ Shopping cart with bundle discounts  
✅ Take tests with timer  
✅ View results and solutions  
✅ Track progress and history

### Payment
✅ Razorpay integration (TEST mode)  
✅ Bundle discounts (10%, 15%, 25%)  
✅ Payment verification  
✅ Purchase history

---

## 📁 Important Files

### Documentation
- `SESSION_SUMMARY.md` - Complete session changes
- `GCP_DEPLOYMENT_GUIDE.md` - Full deployment guide
- `QUICK_DEPLOYMENT_CHECKLIST.md` - Deployment checklist
- `ADMIN_SETUP.md` - Admin account guide
- `CHANGELOG.md` - Version history
- `auth_testing.md` - OAuth testing guide

### Configuration
- `backend/.env` - Backend environment variables
- `frontend/.env` - Frontend environment variables

### Scripts
- `create_admin.py` - Admin account creation
- `deployment-scripts/setup-server.sh` - Server setup
- `deployment-scripts/deploy-app.sh` - Deploy application
- `deployment-scripts/update-app.sh` - Update deployment

---

## 🔧 Configuration

### Backend Environment Variables
```bash
# Database
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"

# Security
SECRET_KEY="your-secret-key"
ENVIRONMENT="development"  # or "production"

# Email (GoDaddy)
SMTP_SERVER="smtpout.secureserver.net"
SMTP_PORT="587"
SMTP_USERNAME="admin@perspectiveupsc.com"
SMTP_PASSWORD="your-password"

# Payment (Razorpay - TEST)
RAZORPAY_KEY_ID="rzp_test_..."
RAZORPAY_KEY_SECRET="your-secret"
```

### Frontend Environment Variables
```bash
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## 🧪 Testing

### Test Google OAuth
1. Go to login page
2. Click "Sign in with Google"
3. Complete Google authentication
4. Should redirect to student dashboard

### Test Razorpay Payment
1. Login as student
2. Browse available tests
3. Click "Buy Now"
4. Use Razorpay test cards:
   - Card: 4111 1111 1111 1111
   - CVV: Any 3 digits
   - Expiry: Any future date

### Test Admin Features
1. Login with admin credentials
2. Create a new test
3. Upload questions via Excel
4. View analytics

---

## 🚀 Deployment

### Option 1: Emergent Platform
Use the "Save to GitHub" feature in your chat interface

### Option 2: Google Cloud VM
```bash
# Follow complete guide
See: GCP_DEPLOYMENT_GUIDE.md

# Or use quick scripts
./deployment-scripts/setup-server.sh
./deployment-scripts/deploy-app.sh
```

### Option 3: Manual Git Push
```bash
git add .
git commit -m "Add Google OAuth and deployment docs"
git push origin main
```

---

## 🐛 Troubleshooting

### Backend Not Starting
```bash
# Check logs
tail -f /var/log/supervisor/backend.err.log

# Restart
sudo supervisorctl restart backend
```

### Frontend Build Errors
```bash
cd /app/frontend
rm -rf node_modules
yarn install
yarn build
```

### Database Issues
```bash
# Check MongoDB
sudo systemctl status mongod

# Restart MongoDB
sudo systemctl restart mongod

# Check connection
mongosh test_database
```

### Admin Can't Login
```bash
# Recreate admin
python3 /app/create_admin.py

# Check database
mongosh test_database --eval "db.users.find({role: 'admin'}).pretty()"
```

### Google OAuth Not Working
1. Check backend logs for errors
2. Verify session_id is being passed
3. Check Emergent API connectivity
4. See `auth_testing.md` for detailed debugging

---

## 📊 Database Collections

### users
- User accounts (admin and students)
- Fields: id, email, name, password, role, is_active

### user_sessions
- OAuth session tokens
- 7-day expiry

### tests
- Test content and questions
- Created by admins

### purchases
- Student test purchases
- Payment records

### carts
- Shopping cart items
- Bundle calculations

### test_results
- Student test results
- Scores and answers

---

## 💡 Tips

### For Development
- Use `--reload` flag with uvicorn for hot reload
- Frontend has hot reload by default
- Check browser console for frontend errors

### For Production
- Change `ENVIRONMENT` to "production"
- Use Razorpay live keys
- Enable MongoDB authentication
- Setup SSL certificates
- Change default admin password

### For Debugging
- Enable detailed logging in backend
- Use browser DevTools Network tab
- Check backend logs in real-time
- Test API endpoints with `/docs` or curl

---

## 🔗 Useful Links

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [MongoDB Docs](https://docs.mongodb.com/)
- [Razorpay Docs](https://razorpay.com/docs/)

### Platform
- [Emergent Platform](https://app.emergent.sh/)
- [Google Cloud Console](https://console.cloud.google.com/)

---

## ✅ Checklist Before Deployment

- [ ] Admin account created and tested
- [ ] Google OAuth tested manually
- [ ] Razorpay payment tested
- [ ] All environment variables configured
- [ ] Database collections verified
- [ ] Frontend build successful
- [ ] Backend logs clean (no errors)
- [ ] SSL certificate obtained (production)
- [ ] DNS configured (production)
- [ ] Backup strategy in place

---

## 📞 Support

### Self-Help
1. Check `SESSION_SUMMARY.md` for recent changes
2. Review `CHANGELOG.md` for version history
3. See deployment guides for setup issues
4. Check testing playbooks for debugging

### Platform Support
- Use Emergent platform support for deployment issues
- Check GitHub issues for code-related problems

---

**Ready to deploy?** Follow `GCP_DEPLOYMENT_GUIDE.md` for step-by-step instructions! 🚀

---

**Version:** Development (October 2025)  
**Status:** ✅ Production Ready  
**Last Updated:** October 23, 2025
