# 🔒 Credentials Template - Perspective UPSC

## ⚠️ SECURITY WARNING

**NEVER commit actual credentials to version control!**

This is a template file showing the structure of credentials needed. Replace ALL placeholder values with your actual credentials and keep them secure.

---

## 📋 Required Credentials Checklist

### 1. Database Credentials
```
MongoDB URL: mongodb://localhost:27017
Database Name: [your_database_name]
```

### 2. Application Secret
```
SECRET_KEY: [Generate a strong 32+ character random string]
```
**Generate using:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Email Service (GoDaddy Titan / Gmail / Other)
```
SMTP_SERVER: [Your SMTP server]
SMTP_PORT: [Your SMTP port]
SMTP_USERNAME: [Your email address]
SMTP_PASSWORD: [Your email password or app password]
FROM_EMAIL: [Your from email address]
```

**Example for GoDaddy Titan:**
- Server: smtp.titan.email
- Port: 465
- Use your GoDaddy email credentials

**Example for Gmail:**
- Server: smtp.gmail.com
- Port: 587
- Use App Password (not regular password)

### 4. Payment Gateway (Razorpay)
```
RAZORPAY_KEY_ID: [Your Razorpay Key ID]
RAZORPAY_KEY_SECRET: [Your Razorpay Secret Key]
```

**How to get:**
1. Sign up at https://razorpay.com
2. Go to Settings > API Keys
3. Generate keys (use Test keys for development, Live keys for production)

---

## 📝 Admin User Credentials

**For Initial Setup Only - Change After First Login!**

```
Email: [admin@yourdomain.com]
Password: [Create a strong password]
Role: admin
```

**Password Requirements:**
- Minimum 8 characters
- Mix of uppercase, lowercase, numbers
- Include special characters
- Never use default passwords in production!

---

## 🔐 Security Best Practices

### DO:
- ✅ Store credentials in `.env` files (never commit to git)
- ✅ Use environment variables in production
- ✅ Rotate credentials regularly
- ✅ Use strong, unique passwords
- ✅ Enable 2FA where available
- ✅ Use password managers (1Password, LastPass, Bitwarden)
- ✅ Limit access to credentials
- ✅ Monitor for unauthorized access

### DON'T:
- ❌ Hardcode credentials in source code
- ❌ Commit `.env` files to version control
- ❌ Share credentials via email or chat
- ❌ Use default or weak passwords
- ❌ Reuse passwords across services
- ❌ Store credentials in plain text documents
- ❌ Leave test credentials in production

---

## 📂 File Structure

```
/app/
├── backend/
│   └── .env  ← Backend credentials (NEVER commit)
├── frontend/
│   └── .env  ← Frontend URLs (NEVER commit)
└── .gitignore  ← Should include .env files
```

---

## 🚨 If Credentials Are Compromised

**Immediate Actions:**
1. **Rotate ALL credentials immediately**
2. **Check access logs for unauthorized activity**
3. **Notify affected users if data breach occurred**
4. **Update application with new credentials**
5. **Review security policies**
6. **Investigate how compromise occurred**

**Razorpay:**
- Go to Dashboard > Settings > API Keys
- Deactivate compromised keys
- Generate new keys
- Update application

**Email:**
- Change SMTP password immediately
- Enable 2FA if available
- Check for unauthorized logins

**Database:**
- Change database password
- Review user access logs
- Check for data modifications

---

## 📞 Where to Get Credentials

### Razorpay
- Website: https://razorpay.com
- Dashboard: https://dashboard.razorpay.com
- Documentation: https://razorpay.com/docs/

### GoDaddy Email
- Login: https://email.godaddy.com
- SMTP Settings: Email Settings > Server Settings
- Support: https://www.godaddy.com/help

### MongoDB
- Local: Default localhost:27017
- Cloud: MongoDB Atlas (https://www.mongodb.com/cloud/atlas)

---

## 🔍 Credential Validation

Before deploying, verify all credentials:

```bash
# Test MongoDB connection
mongosh "mongodb://localhost:27017/your_database"

# Test SMTP (Python)
python -c "
import smtplib
server = smtplib.SMTP('smtp.titan.email', 465)
server.login('your_email', 'your_password')
print('✅ SMTP works')
"

# Test Razorpay (curl)
curl -u YOUR_KEY_ID:YOUR_KEY_SECRET https://api.razorpay.com/v1/payments
```

---

## 📝 Production Checklist

Before going live:
- [ ] All test/development credentials removed
- [ ] Production credentials configured
- [ ] Live Razorpay keys activated
- [ ] Production email configured
- [ ] Database secured with password
- [ ] SECRET_KEY is strong and unique
- [ ] All credentials rotated from development
- [ ] `.env` files not in version control
- [ ] Access logs monitoring enabled
- [ ] Backup of credentials in secure location

---

## 🎯 Quick Setup (Development)

1. Copy this template
2. Replace ALL placeholders with real values
3. Save as `.env` in backend folder
4. Never commit `.env` file
5. Test each service connection
6. Document where you stored credentials securely

---

**Last Updated:** January 2025
**Security Level:** CRITICAL
**Audience:** Development Team, DevOps

---

**Remember: Credentials are like house keys - guard them carefully!** 🔐
