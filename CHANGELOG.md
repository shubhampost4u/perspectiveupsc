# Changelog - PerspectiveUPSC Platform

All notable changes to this project will be documented in this file.

---

## [Unreleased] - 2025-10-23

### 🎉 Added

#### Deployment & Documentation
- **GCP_DEPLOYMENT_GUIDE.md** - Complete 11-part deployment guide for Google Cloud VM
- **QUICK_DEPLOYMENT_CHECKLIST.md** - Quick reference deployment checklist
- **deployment-scripts/** - Automated deployment scripts
  - `setup-server.sh` - Server dependency installation
  - `deploy-app.sh` - Application deployment automation
  - `update-app.sh` - Quick update deployment
  - `create_admin.py` - Admin user creation script
  - `README.md` - Script documentation
- **.github/workflows/deploy.yml** - CI/CD pipeline for automated deployments
- **ADMIN_SETUP.md** - Admin account management guide
- **auth_testing.md** - OAuth testing playbook
- **SESSION_SUMMARY.md** - Complete session documentation
- **CHANGELOG.md** - This file

#### Authentication Features
- **Google OAuth Integration** - Complete sign-in with Google using Emergent service
  - New component: `GoogleAuthCallback.js`
  - Backend endpoint: `POST /api/auth/google`
  - Backend endpoint: `GET /api/auth/me`
  - Session management with 7-day expiry
  - Automatic student account creation for new users
  - Environment-aware cookie configuration

#### Admin Features
- **Admin Creation Script** - `create_admin.py` for easy admin account setup
  - Default credentials: perspectiveupsc1@gmail.com / perspective@2025
  - Custom credentials support
  - Duplicate prevention
  - Proper password hashing

#### Payment Integration
- **Razorpay Script** - Added Razorpay Checkout script to frontend
- **Payment Verification** - Backend tested and confirmed working

### 🔧 Changed

#### Backend (`server.py`)
- **User Model** (Line 92)
  - Changed password field from required to optional
  - Default value: empty string for OAuth users
  - Supports both email/password and OAuth users

- **Authentication System**
  - Updated `HTTPBearer` to optional (`auto_error=False`)
  - Added `get_current_user_flexible()` supporting both JWT and session tokens
  - Added `get_user_by_session_token()` for session-based auth
  - Added `get_emergent_user_data()` for Emergent API integration

- **Session Management**
  - Renamed collection from `sessions` to `user_sessions`
  - Added proper timezone handling for datetime comparisons
  - 7-day session token expiry
  - HttpOnly cookies for security

- **Environment Configuration**
  - Added `ENVIRONMENT` variable (development/production)
  - Added `IS_PRODUCTION` flag for environment-aware settings
  - Cookie security based on environment

- **Logout Endpoint**
  - Updated to use `user_sessions` collection
  - Environment-aware cookie deletion

#### Frontend

- **App.js**
  - Added `GoogleAuthCallback` import
  - Added route: `/auth/google/callback`

- **LoginPage.js**
  - Updated `handleGoogleSignIn()` redirect URL
  - Changed from `/profile` to `/auth/google/callback`

- **index.html**
  - Added Razorpay Checkout script tag

#### Environment Files

- **backend/.env**
  - Added `ENVIRONMENT="development"`

### 🐛 Fixed

#### Critical Bug Fixes
1. **User Model Validation Error**
   - Fixed Pydantic validation failures for users without password
   - Updated 6 locations using `User(**user_data)`
   - All existing users in database updated with password field

2. **HTTPBearer Authentication Blocking**
   - Changed HTTPBearer to allow optional authentication
   - Fixed session token authentication
   - Both JWT and session tokens now work correctly

3. **Timezone DateTime Comparison Error**
   - Fixed "can't compare offset-naive and offset-aware datetimes"
   - Updated `get_user_by_session_token()` with proper timezone handling
   - All datetime operations now timezone-aware

4. **Admin Login Issue**
   - Created missing admin user in database
   - Added required `is_active` field
   - Admin can now login successfully

### 🔒 Security

- Session tokens stored as httpOnly cookies
- Environment-aware cookie security (secure flag)
- 7-day session expiry with automatic cleanup
- Password field optional but properly hashed when present
- Admin creation script uses bcrypt for password hashing

### 📝 Documentation

- Complete GCP deployment guide (11 parts)
- Quick deployment checklist (10 phases)
- Admin account setup instructions
- OAuth testing playbook with manual steps
- Deployment script documentation
- CI/CD workflow template
- Session summary with all changes

### ✅ Verified

- ✅ Razorpay backend: Test order created successfully
- ✅ Razorpay frontend: PaymentDialog component working
- ✅ Admin login: Working with created admin user
- ✅ Backend logs: No errors after fixes
- ✅ Session authentication: Functional with cookies
- ✅ Google OAuth backend: Endpoints responding correctly

---

## Database Schema Changes

### Users Collection
```javascript
{
  id: String,           // UUID
  email: String,        // Email address
  name: String,         // User name
  password: String,     // Optional (empty for OAuth), hashed for email/password
  role: String,         // "admin" or "student"
  is_active: Boolean,   // Account status
  created_at: DateTime  // Timezone-aware
}
```

### User Sessions Collection (new)
```javascript
{
  id: String,                  // UUID
  user_id: String,            // References users.id
  session_token: String,      // 7-day session token
  emerent_session_id: String, // Emergent session ID
  expires_at: DateTime,       // Timezone-aware, 7 days from creation
  created_at: DateTime        // Timezone-aware
}
```

---

## API Changes

### New Endpoints
- `POST /api/auth/google` - Process Google OAuth callback
- `GET /api/auth/me` - Get current authenticated user (alias for /me)

### Modified Endpoints
- `POST /api/logout` - Now clears user_sessions instead of sessions
- All protected endpoints now support session token authentication

---

## Configuration

### Backend Environment Variables
```bash
# New
ENVIRONMENT="development"  # or "production"

# Existing (verified)
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
SECRET_KEY="..."
RAZORPAY_KEY_ID="rzp_test_..."
RAZORPAY_KEY_SECRET="..."
SMTP_SERVER="smtpout.secureserver.net"
SMTP_PORT="587"
SMTP_USERNAME="admin@perspectiveupsc.com"
SMTP_PASSWORD="..."
```

### Frontend Environment Variables
```bash
# Existing (no changes)
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## Migration Notes

### For Existing Users
1. All existing users have been updated with password field
2. Admin account created: perspectiveupsc1@gmail.com
3. Session collection renamed from `sessions` to `user_sessions`

### For New Deployments
1. Use `create_admin.py` to create admin account
2. Configure `ENVIRONMENT` variable in backend/.env
3. Follow GCP_DEPLOYMENT_GUIDE.md for cloud deployment
4. Use deployment scripts for automation

---

## Testing

### Manual Testing Required
- [ ] Google OAuth sign-in flow
- [ ] Razorpay payment with test cards
- [ ] Admin dashboard access
- [ ] Student registration and login

### Automated Testing
- Testing agents available for backend and frontend testing
- Use `auth_testing.md` for OAuth testing scenarios

---

## Known Issues

### Minor
- Google OAuth requires actual Google authentication (can't be fully automated in testing)
- Razorpay in TEST mode (no real transactions)

### None Critical
- Email delivery might face restrictions with some SMTP providers

---

## Deployment

### Development
```bash
# Backend
cd /app/backend
source venv/bin/activate
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Frontend
cd /app/frontend
yarn start
```

### Production
```bash
# Follow GCP_DEPLOYMENT_GUIDE.md
# Or use automated scripts:
./deployment-scripts/setup-server.sh
./deployment-scripts/deploy-app.sh
```

---

## Contributors

- **Main Development Session:** October 23, 2025
- **Platform:** Emergent.sh
- **Stack:** React + FastAPI + MongoDB

---

## Support

For issues or questions:
1. Check `SESSION_SUMMARY.md` for detailed changes
2. Review `GCP_DEPLOYMENT_GUIDE.md` for deployment
3. See `ADMIN_SETUP.md` for admin issues
4. Use `auth_testing.md` for OAuth debugging

---

**Status:** ✅ Ready for deployment  
**Version:** Development (pre-release)  
**Next:** Production deployment to www.perspectiveupsc.com
