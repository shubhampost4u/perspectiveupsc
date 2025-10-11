# 👤 Admin Account Setup Guide

## Problem
After a fresh deployment or database cleanup, the admin account may not exist in the database, preventing administrator login.

---

## Solution: Create Admin User

We've provided a script to easily create an admin user in the database.

### Quick Setup (Default Credentials)

```bash
cd /app
python3 create_admin.py
```

**Default credentials:**
- **Email:** perspectiveupsc1@gmail.com
- **Password:** perspective@2025

### Custom Admin Credentials

```bash
python3 create_admin.py <email> <password> <name>
```

**Example:**
```bash
python3 create_admin.py admin@perspectiveupsc.com MySecurePass123 "Admin Name"
```

---

## For Production Deployment (Google Cloud VM)

After deploying to your GCP VM, create the admin user:

```bash
# SSH to your server
gcloud compute ssh perspectiveupsc-server

# Navigate to app directory
cd /var/www/perspectiveupsc

# Create admin user
python3 create_admin.py

# Or with custom credentials
python3 create_admin.py your-admin@domain.com YourSecurePassword "Your Name"
```

---

## Verify Admin Account

### Check in MongoDB:
```bash
mongosh test_database --quiet --eval "db.users.find({role: 'admin'}, {password: 0}).pretty()"
```

### Test Login via API:
```bash
curl -X POST http://localhost:8001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"perspectiveupsc1@gmail.com","password":"perspective@2025"}'
```

### Test in Browser:
1. Go to your application URL
2. Click "Login"
3. Use the admin credentials
4. You should see the Admin Dashboard

---

## Troubleshooting

### "Admin user already exists"
If you see this message, the admin user is already in the database. Try logging in with the existing credentials.

### "Incorrect email or password"
1. Verify you're using the correct database:
   ```bash
   grep DB_NAME backend/.env
   ```

2. Check if admin user exists:
   ```bash
   mongosh test_database --quiet --eval "db.users.find({email: 'perspectiveupsc1@gmail.com'}).count()"
   ```

3. If needed, delete and recreate:
   ```bash
   mongosh test_database --quiet --eval "db.users.deleteOne({email: 'perspectiveupsc1@gmail.com'})"
   python3 create_admin.py
   ```

### "Module not found" errors
Make sure you're using the Python environment with required packages:
```bash
cd /app/backend
source venv/bin/activate  # If using virtual environment
cd /app
python3 create_admin.py
```

---

## Security Best Practices

### 1. Change Default Password
**⚠️ IMPORTANT:** Always change the default password for production!

```bash
# Create admin with strong password
python3 create_admin.py admin@yourdomain.com 'StrongP@ssw0rd!2025' "Admin Name"
```

### 2. Use Strong Passwords
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, and symbols
- Avoid common words or patterns

### 3. Secure Password Storage
- Never commit passwords to version control
- Use environment variables for sensitive data
- Keep your .env files secure

### 4. Regular Password Changes
Change admin password periodically through the application's password reset feature.

---

## What the Script Does

1. ✅ Connects to MongoDB database specified in environment variables
2. ✅ Checks if admin user already exists (prevents duplicates)
3. ✅ Hashes the password securely using bcrypt
4. ✅ Creates admin user with role "admin"
5. ✅ Sets is_active to true
6. ✅ Generates unique UUID for user ID
7. ✅ Adds timestamp for created_at field
8. ✅ Inserts user into database
9. ✅ Displays confirmation with credentials

---

## Script Location

The admin creation script is available in two locations:

1. **Development:** `/app/create_admin.py`
2. **Deployment Scripts:** `/app/deployment-scripts/create_admin.py`

Both are identical - use whichever is more convenient for your workflow.

---

## Adding to Deployment Workflow

### Include in your deployment checklist:

```bash
# After deploying application
cd /var/www/perspectiveupsc

# Create admin user
python3 create_admin.py

# Verify login works
curl -X POST http://localhost:8001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"perspectiveupsc1@gmail.com","password":"perspective@2025"}'
```

### Or add to your deployment script:

```bash
# In deploy-app.sh, add:
echo "👤 Creating admin user..."
python3 create_admin.py
```

---

## Multiple Admin Users

You can create multiple admin users:

```bash
# First admin
python3 create_admin.py admin1@perspectiveupsc.com Pass123 "Admin One"

# Second admin
python3 create_admin.py admin2@perspectiveupsc.com Pass456 "Admin Two"

# Third admin
python3 create_admin.py admin3@perspectiveupsc.com Pass789 "Admin Three"
```

All admin users will have full administrative access to:
- Create/edit/delete tests
- View all students
- Access analytics
- Bulk upload questions
- Manage purchases

---

## Database Configuration

The script automatically uses environment variables:

```bash
# From backend/.env
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
```

If you need to use different database settings:

```bash
# Temporary override
MONGO_URL="mongodb://localhost:27017" DB_NAME="production_db" python3 create_admin.py
```

---

## Support

If you encounter issues:

1. Check backend logs: `tail -f /var/log/supervisor/backend.err.log`
2. Verify MongoDB is running: `sudo systemctl status mongod`
3. Check database name in `.env` file
4. Ensure all dependencies are installed

---

**🎉 Once admin is created, you can log in and start managing your PerspectiveUPSC platform!**
