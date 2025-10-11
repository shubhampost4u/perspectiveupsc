#!/usr/bin/env python3
"""
Script to create admin user for PerspectiveUPSC
"""
import sys
import os
from datetime import datetime, timezone
from passlib.context import CryptContext
from pymongo import MongoClient
import uuid

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user(email, password, name):
    """Create an admin user in the database"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017/perspectiveupsc")
    client = MongoClient(mongo_url)
    db = client.get_database()
    
    # Check if admin already exists
    existing_admin = db.users.find_one({"email": email})
    if existing_admin:
        print(f"❌ Admin user with email {email} already exists!")
        print(f"   User ID: {existing_admin['id']}")
        print(f"   Role: {existing_admin['role']}")
        return False
    
    # Hash password
    hashed_password = pwd_context.hash(password)
    
    # Create admin user
    admin_user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "password": hashed_password,
        "name": name,
        "role": "admin",
        "created_at": datetime.now(timezone.utc)
    }
    
    # Insert into database
    result = db.users.insert_one(admin_user)
    
    if result.inserted_id:
        print("✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Name: {name}")
        print(f"   Role: admin")
        print(f"   User ID: {admin_user['id']}")
        print(f"\n🔑 Login credentials:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        return True
    else:
        print("❌ Failed to create admin user")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("PerspectiveUPSC - Admin User Creation")
    print("=" * 50)
    print()
    
    # Get admin details
    if len(sys.argv) >= 4:
        email = sys.argv[1]
        password = sys.argv[2]
        name = sys.argv[3]
    else:
        # Default admin credentials
        email = "perspectiveupsc1@gmail.com"
        password = "perspective@2025"
        name = "Admin User"
        
        print(f"📝 Using default admin credentials:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Name: {name}")
        print()
        print("   To use custom credentials, run:")
        print("   python3 create_admin.py <email> <password> <name>")
        print()
    
    # Create admin
    create_admin_user(email, password, name)
    print()
