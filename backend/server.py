from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File, Request, Response, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import pandas as pd
from io import BytesIO
import razorpay
import aiohttp
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from fastapi.responses import StreamingResponse

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security setup
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
IS_PRODUCTION = ENVIRONMENT == 'production'

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)  # Make it optional to allow session auth

# Email configuration
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
FROM_EMAIL = os.environ.get('FROM_EMAIL')

# Create the main app without a prefix
app = FastAPI(title="Test Platform API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ===== MODELS =====
class UserRole(str):
    ADMIN = "admin"
    STUDENT = "student"

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str = UserRole.STUDENT

class UserCreate(UserBase):
    password: str
    # Remove role field - all registrations will be students only

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class PaymentOrder(BaseModel):
    test_id: str
    amount: float  # Amount in rupees

class PaymentVerification(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    password: str = ""  # Default empty string for OAuth users
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    options: List[str]  # 4 options
    correct_answer: int  # Index of correct option (0-3)
    explanation: Optional[str] = None

class QuestionCreate(BaseModel):
    question_text: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None

class Test(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    price: float
    duration_minutes: int
    questions: List[Question]
    created_by: str  # admin user id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class TestCreate(BaseModel):
    title: str
    description: str
    price: float
    duration_minutes: int
    questions: List[QuestionCreate]

class TestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    questions: Optional[List[QuestionCreate]] = None

class TestResponse(BaseModel):
    id: str
    title: str
    description: str
    price: float
    duration_minutes: int
    questions_count: int
    created_at: datetime

class Purchase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    test_id: str
    amount: float
    status: str = "pending"  # pending, completed, failed
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class TestResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    test_id: str
    answers: List[int]  # Student's selected options
    score: int
    total_questions: int
    time_taken_minutes: int
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CartItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_id: str
    test_title: str
    test_price: float
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Cart(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    items: List[CartItem] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CartResponse(BaseModel):
    id: str
    items: List[CartItem]
    subtotal: float
    discount: float
    total: float
    savings: float
    bundle_info: str

class BundleOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    test_ids: List[str]
    individual_total: float
    discount_amount: float
    final_total: float
    status: str = "pending"  # pending, completed, failed
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class AddToCartRequest(BaseModel):
    test_id: str

class CartCheckoutRequest(BaseModel):
    pass  # No additional data needed for cart checkout

class SessionData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    emerent_session_id: str
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GoogleAuthRequest(BaseModel):
    session_id: str

class GoogleAuthResponse(BaseModel):
    access_token: str
    user: UserResponse

# ===== UTILITY FUNCTIONS =====
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def calculate_bundle_discount(items: List[CartItem]) -> Dict[str, Any]:
    """Calculate bundle discount based on number of items"""
    if not items:
        return {
            "subtotal": 0.0,
            "discount_percentage": 0,
            "discount_amount": 0.0,
            "total": 0.0,
            "savings": 0.0,
            "bundle_info": "Empty cart"
        }
    
    subtotal = sum(item.test_price for item in items)
    item_count = len(items)
    
    # Bundle discount logic
    if item_count >= 5:
        discount_percentage = 25  # 25% off for 5+ tests
        bundle_info = "Mega Bundle: 25% OFF on 5+ tests!"
    elif item_count >= 3:
        discount_percentage = 15  # 15% off for 3-4 tests
        bundle_info = "Super Bundle: 15% OFF on 3+ tests!"
    elif item_count >= 2:
        discount_percentage = 10  # 10% off for 2 tests
        bundle_info = "Bundle Deal: 10% OFF on 2+ tests!"
    else:
        discount_percentage = 0
        bundle_info = "Add more tests for bundle discounts!"
    
    discount_amount = (subtotal * discount_percentage) / 100
    total = subtotal - discount_amount
    savings = discount_amount
    
    return {
        "subtotal": round(subtotal, 2),
        "discount_percentage": discount_percentage,
        "discount_amount": round(discount_amount, 2),
        "total": round(total, 2),
        "savings": round(savings, 2),
        "bundle_info": bundle_info
    }

async def send_reset_email(email: str, otp: str) -> bool:
    """Send password reset email with 6-digit OTP"""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.warning("SMTP not configured, password reset email disabled")
        # For demo purposes, just log the OTP
        logger.info(f"Password reset OTP for {email}: {otp}")
        print(f"🔐 Password reset OTP for {email}: {otp}")
        return False
    
    try:
        # Create email message
        subject = "Password Reset OTP - PerspectiveUPSC"
        body = f"""
Hello,

You have requested a password reset for your PerspectiveUPSC account.

Your 6-digit OTP (One-Time Password) is:

    {otp}

Please enter this OTP on the password reset page to set your new password.

⚠️ Important:
- This OTP will expire in 15 minutes
- Do not share this OTP with anyone
- If you didn't request this reset, please ignore this email

Best regards,
PerspectiveUPSC Team
        """
        
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Try multiple SMTP configurations for GoDaddy
        smtp_configs = [
            ("smtpout.secureserver.net", 587, "TLS"),
            ("smtp.secureserver.net", 587, "TLS"), 
            ("smtp.titan.email", 587, "TLS"),
            ("smtp.secureserver.net", 465, "SSL"),
            ("smtp.titan.email", 465, "SSL"),
        ]
        
        last_error = None
        for server, port, method in smtp_configs:
            try:
                logger.info(f"Attempting SMTP connection to {server}:{port} using {method}")
                
                if method == "SSL" and port == 465:
                    with smtplib.SMTP_SSL(server, port, timeout=30) as smtp_server:
                        smtp_server.login(SMTP_USERNAME, SMTP_PASSWORD)
                        smtp_server.send_message(msg)
                        logger.info(f"✅ Successfully sent email via {server}:{port} SSL")
                        return True
                else:
                    with smtplib.SMTP(server, port, timeout=30) as smtp_server:
                        if method == "TLS":
                            smtp_server.starttls()
                        smtp_server.login(SMTP_USERNAME, SMTP_PASSWORD)
                        smtp_server.send_message(msg)
                        logger.info(f"✅ Successfully sent email via {server}:{port} {method}")
                        return True
                        
            except Exception as server_error:
                last_error = server_error
                logger.warning(f"❌ Failed {server}:{port} {method}: {str(server_error)}")
                continue
        
        # If all servers failed
        logger.error(f"❌ All SMTP servers failed for {email}. Last error: {last_error}")
        logger.info(f"Password reset OTP for {email}: {otp}")
        print(f"🔐 Password reset OTP for {email}: {otp}")
        return False
        
    except Exception as e:
        logger.error(f"❌ General error sending reset email to {email}: {str(e)}")
        logger.info(f"Password reset OTP for {email}: {otp}")
        print(f"🔐 Password reset OTP for {email}: {otp}")
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_subject: str = payload.get("sub")
        if token_subject is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Find user by email
    user = await db.users.find_one({"email": token_subject})
    
    if user is None:
        raise credentials_exception
    # Ensure password field exists for Pydantic validation
    if 'password' not in user:
        user['password'] = ""
    return User(**user)

async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# ===== GOOGLE/EMERGENT AUTHENTICATION FUNCTIONS =====
async def get_emergent_user_data(session_id: str) -> Optional[Dict]:
    """Get user data from Emergent authentication service"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"X-Session-ID": session_id}
            async with session.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"Emergent auth API returned status {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error calling Emergent auth API: {str(e)}")
        return None

async def get_user_by_session_token(session_token: str) -> Optional[User]:
    """Get user by session token from database"""
    try:
        session_data = await db.user_sessions.find_one({"session_token": session_token})
        if not session_data:
            return None
        
        # Handle timezone-aware/naive datetime comparison
        expires_at = session_data["expires_at"]
        current_time = datetime.now(timezone.utc)
        
        # If expires_at is timezone-naive, assume it's UTC
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if expires_at < current_time:
            return None
        
        user_data = await db.users.find_one({"id": session_data["user_id"]})
        if user_data:
            # Ensure password field exists for Pydantic validation
            if 'password' not in user_data:
                user_data['password'] = ""
            return User(**user_data)
        return None
    except Exception as e:
        logger.error(f"Error getting user by session token: {str(e)}")
        return None

# Updated authentication dependency to support both JWT and session tokens
async def get_current_user_flexible(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session_token: Optional[str] = Cookie(None)
) -> User:
    """Get current user from JWT token or session token"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try session token first (Google auth)
    if session_token:
        user = await get_user_by_session_token(session_token)
        if user:
            return user
    
    # Fallback to JWT token (email/password auth)
    if authorization:
        token = authorization.credentials
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception
        
        user = await db.users.find_one({"email": email})
        if user is None:
            raise credentials_exception
        # Ensure password field exists for Pydantic validation
        if 'password' not in user:
            user['password'] = ""
        return User(**user)
    
    raise credentials_exception

# ===== AUTHENTICATION ROUTES =====
@api_router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    # Check if email already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_password
    user_data["role"] = UserRole.STUDENT  # Force student role
    
    new_user = User(**user_data)
    await db.users.insert_one(new_user.dict())
    
    return UserResponse(**new_user.dict())



@api_router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    user = await db.users.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    # Create UserResponse directly from database fields
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        is_active=user["is_active"]
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

# ===== GOOGLE AUTHENTICATION ROUTES =====
@api_router.post("/auth/google", response_model=GoogleAuthResponse)
async def google_auth_callback(
    request: GoogleAuthRequest, 
    response: Response
):
    """Handle Google authentication callback from Emergent service"""
    try:
        # Get user data from Emergent authentication service
        emergent_data = await get_emergent_user_data(request.session_id)
        if not emergent_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session ID or authentication failed"
            )
        
        # Extract user data
        email = emergent_data.get("email")
        name = emergent_data.get("name")
        emergent_user_id = emergent_data.get("id")
        session_token = emergent_data.get("session_token")
        
        if not email or not session_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incomplete user data from authentication service"
            )
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": email})
        
        if existing_user:
            # User exists, update session
            # Ensure password field exists for Pydantic validation
            if 'password' not in existing_user:
                existing_user['password'] = ""
            user = User(**existing_user)
        else:
            # Create new user (auto-assign as student for Google auth)
            user_id = str(uuid.uuid4())
            user_data = {
                "id": user_id,
                "email": email,
                "name": name or email.split("@")[0],  # Use email prefix if name not provided
                "password": "",  # No password for Google auth users (empty string)
                "role": UserRole.STUDENT,  # Auto-assign as student
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            }
            
            await db.users.insert_one(user_data)
            user = User(**user_data)
        
        # Create/update session data
        session_data = SessionData(
            user_id=user.id,
            session_token=session_token,
            emerent_session_id=request.session_id
        )
        
        # Store session in database
        await db.user_sessions.update_one(
            {"user_id": user.id},
            {"$set": session_data.dict()},
            upsert=True
        )
        
        # Set session cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            secure=IS_PRODUCTION,  # False for localhost, True for production
            samesite="lax" if not IS_PRODUCTION else "none",  # lax for localhost, none for production
            path="/"
        )
        
        # Also create JWT token for compatibility
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=user.is_active
        )
        
        return GoogleAuthResponse(access_token=access_token, user=user_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Google auth callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication processing failed"
        )

@api_router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user_flexible)):
    """Get user profile (works with both JWT and session auth)"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        is_active=current_user.is_active
    )

@api_router.post("/logout")
async def logout(response: Response, current_user: User = Depends(get_current_user_flexible)):
    """Logout user (clear session token)"""
    try:
        # Remove session from database
        await db.user_sessions.delete_many({"user_id": current_user.id})
        
        # Clear session cookie
        response.delete_cookie(
            key="session_token",
            path="/",
            secure=IS_PRODUCTION,
            samesite="lax" if not IS_PRODUCTION else "none"
        )
        
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@api_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user_flexible)):
    return UserResponse(**current_user.dict())

@api_router.get("/auth/me", response_model=UserResponse)
async def get_auth_user_info(current_user: User = Depends(get_current_user_flexible)):
    """Alias for /me endpoint for auth consistency"""
    return UserResponse(**current_user.dict())

@api_router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset email to user"""
    # Always return the same message for security (don't reveal if email exists)
    user = await db.users.find_one({"email": request.email})
    
    if user and user["role"] == UserRole.STUDENT:
        # Generate 6-digit OTP instead of long token
        otp = f"{secrets.randbelow(900000) + 100000:06d}"
        expiry = datetime.now(timezone.utc) + timedelta(minutes=15)  # Shorter expiry for OTP
        
        # Store reset OTP in database
        await db.password_resets.insert_one({
            "email": request.email,
            "otp": otp,
            "expires_at": expiry,
            "used": False
        })
        
        # Try to send password reset email
        email_sent = await send_reset_email(request.email, otp)
        
        # For development/testing, return OTP when email fails
        if not email_sent:
            return {
                "message": "If the email exists, a password reset OTP has been sent to your email",
                "demo_otp": otp,
                "demo_note": "Email delivery failed. Use this 6-digit OTP for testing purposes.",
                "email_status": "failed"
            }
    
    return {"message": "If the email exists, a password reset OTP has been sent to your email"}

@api_router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset user password using 6-digit OTP"""
    # Find valid reset OTP
    reset_record = await db.password_resets.find_one({
        "email": request.email,
        "otp": request.otp,
        "used": False,
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Update user password
    hashed_password = get_password_hash(request.new_password)
    await db.users.update_one(
        {"email": request.email},
        {"$set": {"password_hash": hashed_password}}
    )
    
    # Mark reset OTP as used
    await db.password_resets.update_one(
        {"_id": reset_record["_id"]},
        {"$set": {"used": True}}
    )
    
    return {"message": "Password reset successfully"}


# ===== PUBLIC ROUTES =====
@api_router.get("/public/tests")
async def get_public_tests():
    """Get all active tests for public display (no authentication required)"""
    try:
        # Get all active tests
        tests = await db.tests.find({"is_active": True}).sort("created_at", -1).to_list(1000)
        
        # Format tests for public display
        public_tests = []
        for test in tests:
            public_tests.append({
                "id": test.get("id"),
                "title": test.get("title"),
                "description": test.get("description"),
                "price": test.get("price"),
                "duration_minutes": test.get("duration_minutes"),
                "total_questions": len(test.get("questions", [])),
                "subject": test.get("subject"),
                "created_at": test.get("created_at")
            })
        
        return public_tests
    except Exception as e:
        logger.error(f"Error fetching public tests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch tests")

# ===== ADMIN ROUTES =====
@api_router.post("/admin/tests", response_model=TestResponse)
async def create_test(test: TestCreate, admin: User = Depends(require_admin)):
    # Convert questions
    questions = [Question(**q.dict()) for q in test.questions]
    
    new_test = Test(
        **test.dict(exclude={"questions"}),
        questions=questions,
        created_by=admin.id
    )
    
    await db.tests.insert_one(new_test.dict())
    
    return TestResponse(
        **new_test.dict(),
        questions_count=len(new_test.questions)
    )

@api_router.get("/admin/tests", response_model=List[TestResponse])
async def get_admin_tests(admin: User = Depends(require_admin)):
    tests = await db.tests.find({"created_by": admin.id}).to_list(1000)
    return [TestResponse(**test, questions_count=len(test["questions"])) for test in tests]

@api_router.delete("/admin/tests/{test_id}")
async def delete_test(test_id: str, admin: User = Depends(require_admin)):
    """Delete a test created by the admin"""
    # Check if test exists and belongs to the admin
    test = await db.tests.find_one({"id": test_id, "created_by": admin.id})
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found or you don't have permission to delete it"
        )
    
    # Check if any students have purchased this test
    purchases = await db.purchases.find_one({"test_id": test_id})
    if purchases:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete test that has been purchased by students"
        )
    
    # Delete the test
    result = await db.tests.delete_one({"id": test_id, "created_by": admin.id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    return {"message": "Test deleted successfully"}

@api_router.put("/admin/tests/{test_id}", response_model=TestResponse)
async def update_test(test_id: str, test_update: TestUpdate, admin: User = Depends(require_admin)):
    """Update a test created by the admin. Can update even if test has been purchased."""
    # Check if test exists and belongs to the admin
    existing_test = await db.tests.find_one({"id": test_id, "created_by": admin.id})
    if not existing_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found or you don't have permission to update it"
        )
    
    # Prepare update data - only include fields that are provided
    update_data = {}
    if test_update.title is not None:
        update_data["title"] = test_update.title
    if test_update.description is not None:
        update_data["description"] = test_update.description
    if test_update.price is not None:
        update_data["price"] = test_update.price
    if test_update.duration_minutes is not None:
        update_data["duration_minutes"] = test_update.duration_minutes
    if test_update.questions is not None:
        # Convert questions
        questions = [Question(**q.dict()) for q in test_update.questions]
        update_data["questions"] = [q.dict() for q in questions]
    
    # Update the test
    if update_data:
        await db.tests.update_one(
            {"id": test_id, "created_by": admin.id},
            {"$set": update_data}
        )
    
    # Fetch and return updated test
    updated_test = await db.tests.find_one({"id": test_id})
    return TestResponse(
        **updated_test,
        questions_count=len(updated_test["questions"])
    )

@api_router.get("/admin/students", response_model=List[UserResponse])
async def get_students(admin: User = Depends(require_admin)):
    students = await db.users.find({"role": UserRole.STUDENT}).to_list(1000)
    return [UserResponse(**student) for student in students]

@api_router.get("/admin/bulk-upload-format")
async def get_bulk_upload_format(admin: User = Depends(require_admin)):
    """Get the format requirements for bulk question upload"""
    return {
        "message": "Excel file format for bulk question upload",
        "required_columns": [
            "question_text",
            "option_a", 
            "option_b",
            "option_c", 
            "option_d",
            "correct_answer",
            "explanation"
        ],
        "format_rules": [
            "Save file as .xlsx format",
            "First row should contain column headers exactly as shown above",
            "question_text: The question content",
            "option_a, option_b, option_c, option_d: The four answer options", 
            "correct_answer: Must be 'A', 'B', 'C', or 'D' (case insensitive)",
            "explanation: Detailed solution explanation for the question",
            "Maximum 120 questions per upload",
            "All fields are required - no empty cells allowed"
        ],
        "sample_data": {
            "question_text": "What is the capital of India?",
            "option_a": "Mumbai",
            "option_b": "New Delhi", 
            "option_c": "Kolkata",
            "option_d": "Chennai",
            "correct_answer": "B",
            "explanation": "New Delhi is the capital city of India. It serves as the seat of all three branches of the Government of India."
        }
    }

@api_router.post("/admin/bulk-upload-questions")
async def bulk_upload_questions(
    file: UploadFile = File(...),
    admin: User = Depends(require_admin)
):
    """Upload questions in bulk from Excel file"""
    
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )
    
    try:
        # Read Excel file
        content = await file.read()
        df = pd.read_excel(BytesIO(content))
        
        # Validate required columns
        required_columns = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'explanation']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Validate data
        if len(df) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Excel file is empty"
            )
        
        if len(df) > 120:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 120 questions allowed per upload"
            )
        
        # Process questions
        questions = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Check for empty cells
                if row.isna().any():
                    errors.append(f"Row {index + 2}: Contains empty cells")
                    continue
                
                # Validate correct answer
                correct_answer = str(row['correct_answer']).upper().strip()
                if correct_answer not in ['A', 'B', 'C', 'D']:
                    errors.append(f"Row {index + 2}: correct_answer must be A, B, C, or D")
                    continue
                
                # Convert correct answer to index
                correct_index = ord(correct_answer) - ord('A')
                
                # Create question
                question = Question(
                    question_text=str(row['question_text']).strip(),
                    options=[
                        str(row['option_a']).strip(),
                        str(row['option_b']).strip(), 
                        str(row['option_c']).strip(),
                        str(row['option_d']).strip()
                    ],
                    correct_answer=correct_index,
                    explanation=str(row['explanation']).strip()
                )
                questions.append(question)
                
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
        
        if errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Validation errors found",
                    "errors": errors[:10],  # Show first 10 errors
                    "total_errors": len(errors)
                }
            )
        
        return {
            "message": f"Successfully processed {len(questions)} questions",
            "questions": [q.dict() for q in questions],
            "count": len(questions)
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Excel file is empty or corrupted"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

# ===== STUDENT ROUTES =====
@api_router.get("/tests", response_model=List[TestResponse])
async def get_available_tests():
    tests = await db.tests.find({"is_active": True}).to_list(1000)
    return [TestResponse(**test, questions_count=len(test["questions"])) for test in tests]

@api_router.post("/tests/{test_id}/purchase")
async def purchase_test(test_id: str, current_user: User = Depends(get_current_user_flexible)):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can purchase tests")
    
    test = await db.tests.find_one({"id": test_id})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Check if already purchased
    existing_purchase = await db.purchases.find_one({
        "student_id": current_user.id,
        "test_id": test_id,
        "status": "completed"
    })
    if existing_purchase:
        raise HTTPException(status_code=400, detail="Test already purchased")
    
    if not razorpay_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment gateway not configured"
        )
    
    # Create Razorpay order
    amount_in_paise = int(test["price"] * 100)  # Convert to paise
    
    try:
        razorpay_order = razorpay_client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "payment_capture": 1
        })
        
        # Store payment order in database
        purchase = Purchase(
            student_id=current_user.id,
            test_id=test_id,
            amount=test["price"],
            status="pending",
            razorpay_order_id=razorpay_order["id"]
        )
        
        await db.purchases.insert_one(purchase.dict())
        
        return {
            "order_id": razorpay_order["id"],
            "amount": amount_in_paise,
            "currency": "INR",
            "key_id": RAZORPAY_KEY_ID,
            "test_title": test["title"],
            "student_name": current_user.name,
            "student_email": current_user.email
        }
        
    except Exception as e:
        logger.error(f"Error creating Razorpay order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment order"
        )

@api_router.post("/verify-payment")
async def verify_payment(
    verification: PaymentVerification,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can verify payments")
    
    if not razorpay_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment gateway not configured"
        )
    
    try:
        # Verify payment signature
        params_dict = {
            'razorpay_order_id': verification.razorpay_order_id,
            'razorpay_payment_id': verification.razorpay_payment_id,
            'razorpay_signature': verification.razorpay_signature
        }
        
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        # Update purchase status
        result = await db.purchases.update_one(
            {
                "student_id": current_user.id,
                "razorpay_order_id": verification.razorpay_order_id,
                "status": "pending"
            },
            {
                "$set": {
                    "status": "completed",
                    "razorpay_payment_id": verification.razorpay_payment_id,
                    "completed_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase record not found"
            )
        
        return {"message": "Payment verified successfully", "status": "success"}
        
    except razorpay.errors.SignatureVerificationError:
        logger.error("Payment signature verification failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment verification failed"
        )
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment verification failed"
        )

@api_router.get("/my-tests", response_model=List[TestResponse])
async def get_purchased_tests(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can view purchased tests")
    
    purchases = await db.purchases.find({
        "student_id": current_user.id,
        "status": "completed"
    }).to_list(1000)
    
    test_ids = [p["test_id"] for p in purchases]
    tests = await db.tests.find({"id": {"$in": test_ids}}).to_list(1000)
    
    return [TestResponse(**test, questions_count=len(test["questions"])) for test in tests]

@api_router.get("/tests/{test_id}/take")
async def get_test_for_taking(test_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can take tests")
    
    # Check if purchased
    purchase = await db.purchases.find_one({
        "student_id": current_user.id,
        "test_id": test_id,
        "status": "completed"
    })
    if not purchase:
        raise HTTPException(status_code=403, detail="Test not purchased")
    
    # Check if already taken
    result = await db.test_results.find_one({
        "student_id": current_user.id,
        "test_id": test_id
    })
    if result:
        raise HTTPException(status_code=400, detail="Test already completed")
    
    test = await db.tests.find_one({"id": test_id})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Return test without correct answers
    questions_for_student = []
    for q in test["questions"]:
        questions_for_student.append({
            "id": q["id"],
            "question_text": q["question_text"],
            "options": q["options"]
        })
    
    return {
        "id": test["id"],
        "title": test["title"],
        "description": test["description"],
        "duration_minutes": test["duration_minutes"],
        "questions": questions_for_student
    }

@api_router.post("/tests/{test_id}/submit")
async def submit_test(
    test_id: str, 
    answers: Dict[str, Any], 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can submit tests")
    
    test = await db.tests.find_one({"id": test_id})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Calculate score
    student_answers = answers["answers"]  # List of selected options
    correct_count = 0
    
    for i, question in enumerate(test["questions"]):
        if i < len(student_answers) and student_answers[i] == question["correct_answer"]:
            correct_count += 1
    
    result = TestResult(
        student_id=current_user.id,
        test_id=test_id,
        answers=student_answers,
        score=correct_count,
        total_questions=len(test["questions"]),
        time_taken_minutes=answers.get("time_taken_minutes", 0)
    )
    
    await db.test_results.insert_one(result.dict())
    
    return {
        "score": correct_count,
        "total_questions": len(test["questions"]),
        "percentage": round((correct_count / len(test["questions"])) * 100, 2)
    }

@api_router.get("/my-results", response_model=List[Dict])
async def get_my_results(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can view results")
    
    results = await db.test_results.find({"student_id": current_user.id}).to_list(1000)
    
    # Get test details for each result
    enriched_results = []
    for result in results:
        test = await db.tests.find_one({"id": result["test_id"]})
        if test:
            enriched_results.append({
                "id": result["id"],
                "test_id": result["test_id"],
                "test_title": test["title"],
                "score": result["score"],
                "total_questions": result["total_questions"],
                "percentage": round((result["score"] / result["total_questions"]) * 100, 2),
                "completed_at": result["completed_at"],
                "time_taken_minutes": result.get("time_taken_minutes", 0)
            })
    
    return enriched_results

@api_router.get("/test-solutions/{test_id}")
async def get_test_solutions(test_id: str, current_user: User = Depends(get_current_user)):
    """Get test solutions and explanations after completing the test"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can view solutions")
    
    # CRITICAL: Check if student has PAID for the test (not just purchased)
    purchase = await db.purchases.find_one({
        "student_id": current_user.id,
        "test_id": test_id,
        "status": "completed"  # MUST be completed payment
    })
    
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must complete the payment before viewing solutions"
        )
    
    # Check if student has completed the test
    result = await db.test_results.find_one({
        "student_id": current_user.id,
        "test_id": test_id
    })
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must complete the test before viewing solutions"
        )
    
    # Get test with questions and solutions
    test = await db.tests.find_one({"id": test_id})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Prepare solutions with student's answers
    solutions = []
    student_answers = result.get("answers", [])
    
    for i, question in enumerate(test["questions"]):
        student_answer = student_answers[i] if i < len(student_answers) else -1
        is_correct = student_answer == question["correct_answer"]
        
        solutions.append({
            "question_number": i + 1,
            "question_text": question["question_text"],
            "options": question["options"],
            "correct_answer": question["correct_answer"],
            "correct_option": question["options"][question["correct_answer"]],
            "student_answer": student_answer,
            "student_option": question["options"][student_answer] if 0 <= student_answer < len(question["options"]) else "Not answered",
            "is_correct": is_correct,
            "explanation": question.get("explanation", "No explanation provided")
        })
    
    return {
        "test_id": test_id,
        "test_title": test["title"],
        "student_score": result["score"],
        "total_questions": result["total_questions"],
        "percentage": round((result["score"] / result["total_questions"]) * 100, 2),
        "completed_at": result["completed_at"],
        "solutions": solutions
    }

@api_router.get("/tests/{test_id}/download-solutions")
async def download_test_solutions_pdf(test_id: str, current_user: User = Depends(get_current_user)):
    """Download test solutions as PDF with watermark"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can download solutions")
    
    # CRITICAL: Check if student has COMPLETED PAYMENT for the test
    purchase = await db.purchases.find_one({
        "student_id": current_user.id,
        "test_id": test_id,
        "status": "completed"  # MUST be completed payment
    })
    
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must complete the payment before downloading solutions"
        )
    
    # Check if student has completed the test
    result = await db.test_results.find_one({
        "student_id": current_user.id,
        "test_id": test_id
    })
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must complete the test before downloading solutions"
        )
    
    # Get test with questions and solutions
    test = await db.tests.find_one({"id": test_id})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#2563eb',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    watermark_style = ParagraphStyle(
        'Watermark',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#9ca3af',
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='#1e40af',
        spaceAfter=12,
        spaceBefore=12
    )
    
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontSize=12,
        textColor='#111827',
        spaceAfter=10,
        alignment=TA_JUSTIFY
    )
    
    option_style = ParagraphStyle(
        'Option',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#374151',
        spaceAfter=6,
        leftIndent=20
    )
    
    explanation_style = ParagraphStyle(
        'Explanation',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#059669',
        spaceAfter=15,
        leftIndent=20,
        alignment=TA_JUSTIFY
    )
    
    # Add watermark and title
    elements.append(Paragraph("PERSPECTIVE UPSC", watermark_style))
    elements.append(Paragraph(f"Test Solutions: {test['title']}", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Add test info
    info_text = f"""<b>Student:</b> {current_user.name}<br/>
    <b>Score:</b> {result['score']}/{result['total_questions']} 
    ({round((result['score'] / result['total_questions']) * 100, 2)}%)<br/>
    <b>Completed:</b> {result['completed_at'].strftime('%B %d, %Y at %I:%M %p')}"""
    elements.append(Paragraph(info_text, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Add divider
    elements.append(Paragraph("<hr/>", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Get student answers
    student_answers = result.get("answers", [])
    
    # Add questions with solutions
    for i, question in enumerate(test["questions"]):
        # Question number and text
        q_number = f"<b>Question {i + 1}:</b>"
        elements.append(Paragraph(q_number, heading_style))
        elements.append(Paragraph(question["question_text"], question_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Options
        student_answer = student_answers[i] if i < len(student_answers) else -1
        correct_answer = question["correct_answer"]
        
        for j, option in enumerate(question["options"]):
            # Mark correct answer in green, wrong answer in red
            if j == correct_answer:
                option_text = f'<font color="#059669"><b>✓ {chr(65+j)}. {option} (Correct Answer)</b></font>'
            elif j == student_answer and j != correct_answer:
                option_text = f'<font color="#dc2626">✗ {chr(65+j)}. {option} (Your Answer)</font>'
            else:
                option_text = f'{chr(65+j)}. {option}'
            
            elements.append(Paragraph(option_text, option_style))
        
        elements.append(Spacer(1, 0.15*inch))
        
        # Explanation
        explanation = question.get("explanation", "No explanation provided")
        explanation_text = f'<b>Explanation:</b><br/>{explanation}'
        elements.append(Paragraph(explanation_text, explanation_style))
        
        # Add separator between questions
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("<hr/>", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
    
    # Add footer watermark
    elements.append(Spacer(1, 0.3*inch))
    footer_text = "© Perspective UPSC - www.perspectiveupsc.com"
    elements.append(Paragraph(footer_text, watermark_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data
    buffer.seek(0)
    
    # Return as downloadable file
    filename = f"{test['title'].replace(' ', '_')}_Solutions.pdf"
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

# ===== CART ROUTES =====
@api_router.get("/cart", response_model=CartResponse)
async def get_cart(current_user: User = Depends(get_current_user)):
    """Get student's current cart"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can access cart")
    
    # Get or create cart
    cart = await db.carts.find_one({"student_id": current_user.id})
    if not cart:
        new_cart = Cart(student_id=current_user.id)
        await db.carts.insert_one(new_cart.dict())
        cart = new_cart.dict()
    
    # Calculate pricing
    bundle_calc = calculate_bundle_discount(
        [CartItem(**item) for item in cart.get("items", [])]
    )
    
    return CartResponse(
        id=cart.get("id", str(cart.get("_id", "unknown"))),
        items=cart.get("items", []),
        subtotal=bundle_calc["subtotal"],
        discount=bundle_calc["discount_amount"],
        total=bundle_calc["total"],
        savings=bundle_calc["savings"],
        bundle_info=bundle_calc["bundle_info"]
    )

@api_router.post("/cart/add")
async def add_to_cart(request: AddToCartRequest, current_user: User = Depends(get_current_user)):
    """Add a test to cart"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can add to cart")
    
    # Check if test exists
    test = await db.tests.find_one({"id": request.test_id, "is_active": True})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Check if already purchased
    existing_purchase = await db.purchases.find_one({
        "student_id": current_user.id,
        "test_id": request.test_id,
        "status": "completed"
    })
    if existing_purchase:
        raise HTTPException(status_code=400, detail="Test already purchased")
    
    # Get or create cart
    cart = await db.carts.find_one({"student_id": current_user.id})
    if not cart:
        cart = Cart(student_id=current_user.id)
        cart_dict = cart.dict()
    else:
        cart_dict = cart
    
    # Check if test already in cart
    existing_items = cart_dict.get("items", [])
    for item in existing_items:
        if item["test_id"] == request.test_id:
            raise HTTPException(status_code=400, detail="Test already in cart")
    
    # Add item to cart
    new_item = CartItem(
        test_id=request.test_id,
        test_title=test["title"],
        test_price=test["price"]
    )
    
    existing_items.append(new_item.dict())
    
    # Update cart
    await db.carts.update_one(
        {"student_id": current_user.id},
        {
            "$set": {
                "items": existing_items,
                "updated_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )
    
    return {"message": "Test added to cart successfully"}

@api_router.delete("/cart/remove/{test_id}")
async def remove_from_cart(test_id: str, current_user: User = Depends(get_current_user)):
    """Remove a test from cart"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can modify cart")
    
    cart = await db.carts.find_one({"student_id": current_user.id})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # Remove item from cart
    existing_items = cart.get("items", [])
    updated_items = [item for item in existing_items if item["test_id"] != test_id]
    
    if len(updated_items) == len(existing_items):
        raise HTTPException(status_code=404, detail="Test not found in cart")
    
    # Update cart
    await db.carts.update_one(
        {"student_id": current_user.id},
        {
            "$set": {
                "items": updated_items,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    return {"message": "Test removed from cart successfully"}

@api_router.delete("/cart/clear")
async def clear_cart(current_user: User = Depends(get_current_user)):
    """Clear all items from cart"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can modify cart")
    
    await db.carts.update_one(
        {"student_id": current_user.id},
        {
            "$set": {
                "items": [],
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    return {"message": "Cart cleared successfully"}

@api_router.post("/cart/checkout")
async def checkout_cart(current_user: User = Depends(get_current_user)):
    """Create Razorpay order for cart checkout"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can checkout")
    
    if not razorpay_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment gateway not configured"
        )
    
    # Get cart
    cart = await db.carts.find_one({"student_id": current_user.id})
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate pricing
    bundle_calc = calculate_bundle_discount(
        [CartItem(**item) for item in cart["items"]]
    )
    
    # Create bundle order record
    bundle_order = BundleOrder(
        student_id=current_user.id,
        test_ids=[item["test_id"] for item in cart["items"]],
        individual_total=bundle_calc["subtotal"],
        discount_amount=bundle_calc["discount_amount"],
        final_total=bundle_calc["total"]
    )
    
    # Create Razorpay order
    try:
        razorpay_order = razorpay_client.order.create({
            "amount": int(bundle_calc["total"] * 100),  # Amount in paise
            "currency": "INR",
            "receipt": bundle_order.id
        })
        
        bundle_order.razorpay_order_id = razorpay_order['id']
        
        # Save bundle order
        await db.bundle_orders.insert_one(bundle_order.dict())
        
        return {
            "order_id": razorpay_order['id'],
            "amount": bundle_calc["total"],
            "currency": "INR",
            "bundle_info": bundle_calc["bundle_info"],
            "savings": bundle_calc["savings"],
            "test_count": len(cart["items"])
        }
        
    except Exception as e:
        logger.error(f"Error creating Razorpay order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment order"
        )

@api_router.post("/cart/verify-payment")
async def verify_cart_payment(verification: PaymentVerification, current_user: User = Depends(get_current_user)):
    """Verify cart payment and complete bundle purchase"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can verify payments")
    
    if not razorpay_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment gateway not configured"
        )
    
    try:
        # Verify payment signature
        params_dict = {
            'razorpay_order_id': verification.razorpay_order_id,
            'razorpay_payment_id': verification.razorpay_payment_id,
            'razorpay_signature': verification.razorpay_signature
        }
        
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        # Update bundle order status
        bundle_order = await db.bundle_orders.find_one_and_update(
            {
                "student_id": current_user.id,
                "razorpay_order_id": verification.razorpay_order_id,
                "status": "pending"
            },
            {
                "$set": {
                    "status": "completed",
                    "razorpay_payment_id": verification.razorpay_payment_id,
                    "completed_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if not bundle_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bundle order not found"
            )
        
        # Create individual purchase records for each test
        purchases = []
        for test_id in bundle_order["test_ids"]:
            purchase = Purchase(
                student_id=current_user.id,
                test_id=test_id,
                amount=bundle_order["final_total"] / len(bundle_order["test_ids"]),  # Split amount evenly
                status="completed",
                razorpay_order_id=verification.razorpay_order_id,
                razorpay_payment_id=verification.razorpay_payment_id,
                completed_at=datetime.now(timezone.utc)
            )
            purchases.append(purchase.dict())
        
        # Insert all purchases
        await db.purchases.insert_many(purchases)
        
        # Clear the cart
        await db.carts.update_one(
            {"student_id": current_user.id},
            {
                "$set": {
                    "items": [],
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return {
            "message": "Bundle payment verified successfully",
            "status": "success",
            "tests_purchased": len(bundle_order["test_ids"]),
            "total_savings": bundle_order["discount_amount"]
        }
        
    except razorpay.errors.SignatureVerificationError:
        logger.error("Bundle payment signature verification failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment verification failed"
        )
    except Exception as e:
        logger.error(f"Error verifying bundle payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment verification failed"
        )

@api_router.get("/debug-users")
async def debug_users():
    """Debug endpoint to check users in database"""
    users = await db.users.find({}).to_list(100)
    result = []
    for user in users:
        result.append({
            "email": user.get("email"),
            "role": user.get("role"),
            "id": user.get("id"),
            "name": user.get("name")
        })
    return {"users": result, "count": len(result)}


# ===== ANALYTICS ENDPOINTS =====

@api_router.get("/admin/analytics/overview")
async def get_analytics_overview(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin: User = Depends(require_admin)
):
    """Get comprehensive analytics overview"""
    try:
        # Parse dates
        if start_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        else:
            start = datetime.now(timezone.utc) - timedelta(days=30)
        
        if end_date:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        else:
            end = datetime.now(timezone.utc)
        
        # Total revenue (all time)
        total_revenue_result = await db.purchases.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(1)
        total_revenue = total_revenue_result[0]["total"] if total_revenue_result else 0
        
        # Revenue in date range
        period_revenue_result = await db.purchases.aggregate([
            {"$match": {"created_at": {"$gte": start, "$lte": end}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(1)
        period_revenue = period_revenue_result[0]["total"] if period_revenue_result else 0
        
        # Today's revenue
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_revenue_result = await db.purchases.aggregate([
            {"$match": {"created_at": {"$gte": today_start}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(1)
        today_revenue = today_revenue_result[0]["total"] if today_revenue_result else 0
        
        # This month's revenue
        month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_revenue_result = await db.purchases.aggregate([
            {"$match": {"created_at": {"$gte": month_start}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(1)
        month_revenue = month_revenue_result[0]["total"] if month_revenue_result else 0
        
        # Total orders
        total_orders = await db.purchases.count_documents({})
        period_orders = await db.purchases.count_documents({
            "created_at": {"$gte": start, "$lte": end}
        })
        
        # Average order value
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Total students
        total_students = await db.users.count_documents({"role": "student"})
        
        # New students in period
        new_students = await db.users.count_documents({
            "role": "student",
            "created_at": {"$gte": start, "$lte": end}
        })
        
        # Active users (last 7 days)
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        active_users_7d = await db.test_results.distinct("user_id", {
            "submitted_at": {"$gte": week_ago}
        })
        
        # Active users (last 30 days)
        month_ago = datetime.now(timezone.utc) - timedelta(days=30)
        active_users_30d = await db.test_results.distinct("user_id", {
            "submitted_at": {"$gte": month_ago}
        })
        
        # Total tests
        total_tests = await db.tests.count_documents({})
        
        # Total test attempts
        total_attempts = await db.test_results.count_documents({})
        period_attempts = await db.test_results.count_documents({
            "submitted_at": {"$gte": start, "$lte": end}
        })
        
        return {
            "revenue": {
                "total": round(total_revenue, 2),
                "period": round(period_revenue, 2),
                "today": round(today_revenue, 2),
                "this_month": round(month_revenue, 2),
                "average_order_value": round(avg_order_value, 2)
            },
            "orders": {
                "total": total_orders,
                "period": period_orders
            },
            "students": {
                "total": total_students,
                "new_in_period": new_students,
                "active_7d": len(active_users_7d),
                "active_30d": len(active_users_30d)
            },
            "tests": {
                "total": total_tests,
                "total_attempts": total_attempts,
                "period_attempts": period_attempts
            }
        }
    except Exception as e:
        logger.error(f"Analytics overview error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/analytics/revenue-chart")
async def get_revenue_chart(
    period: str = "daily",  # daily, weekly, monthly
    days: int = 30,
    admin: User = Depends(require_admin)
):
    """Get revenue chart data"""
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        if period == "daily":
            group_format = "%Y-%m-%d"
        elif period == "weekly":
            group_format = "%Y-W%U"
        else:  # monthly
            group_format = "%Y-%m"
        
        pipeline = [
            {"$match": {"created_at": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {
                "_id": {"$dateToString": {"format": group_format, "date": "$created_at"}},
                "revenue": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        results = await db.purchases.aggregate(pipeline).to_list(10000)
        
        return {
            "labels": [r["_id"] for r in results],
            "revenue": [round(r["revenue"], 2) for r in results],
            "orders": [r["count"] for r in results]
        }
    except Exception as e:
        logger.error(f"Revenue chart error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/analytics/top-tests")
async def get_top_tests(
    limit: int = 10,
    admin: User = Depends(require_admin)
):
    """Get top selling tests"""
    try:
        pipeline = [
            {"$group": {
                "_id": "$test_id",
                "revenue": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"revenue": -1}},
            {"$limit": limit}
        ]
        
        results = await db.purchases.aggregate(pipeline).to_list(10000)
        
        # Get test details
        top_tests = []
        for r in results:
            test = await db.tests.find_one({"id": r["_id"]})
            if test:
                top_tests.append({
                    "test_id": r["_id"],
                    "test_name": test.get("title", "Unknown"),
                    "revenue": round(r["revenue"], 2),
                    "sales": r["count"]
                })
        
        return top_tests
    except Exception as e:
        logger.error(f"Top tests error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/analytics/bundle-breakdown")
async def get_bundle_breakdown(admin: User = Depends(require_admin)):
    """Get bundle purchase breakdown"""
    try:
        # Get bundle orders
        bundle_orders = await db.bundle_orders.find({}).to_list(10000)
        
        breakdown = {
            "2-4_tests": {"count": 0, "revenue": 0, "discount_percent": 10},
            "5-9_tests": {"count": 0, "revenue": 0, "discount_percent": 15},
            "10+_tests": {"count": 0, "revenue": 0, "discount_percent": 25}
        }
        
        for order in bundle_orders:
            test_count = len(order.get("test_ids", []))
            amount = order.get("final_amount", 0)
            
            if 2 <= test_count <= 4:
                breakdown["2-4_tests"]["count"] += 1
                breakdown["2-4_tests"]["revenue"] += amount
            elif 5 <= test_count <= 9:
                breakdown["5-9_tests"]["count"] += 1
                breakdown["5-9_tests"]["revenue"] += amount
            elif test_count >= 10:
                breakdown["10+_tests"]["count"] += 1
                breakdown["10+_tests"]["revenue"] += amount
        
        return breakdown
    except Exception as e:
        logger.error(f"Bundle breakdown error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/analytics/user-growth")
async def get_user_growth(
    days: int = 30,
    admin: User = Depends(require_admin)
):
    """Get user registration growth"""
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        pipeline = [
            {"$match": {
                "role": "student",
                "created_at": {"$gte": start_date, "$lte": end_date}
            }},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        results = await db.users.aggregate(pipeline).to_list(10000)
        
        # Fill in missing dates with 0
        all_dates = []
        current = start_date
        while current <= end_date:
            all_dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        
        data_dict = {r["_id"]: r["count"] for r in results}
        
        return {
            "labels": all_dates,
            "registrations": [data_dict.get(date, 0) for date in all_dates]
        }
    except Exception as e:
        logger.error(f"User growth error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/analytics/test-performance")
async def get_test_performance(admin: User = Depends(require_admin)):
    """Get test performance metrics"""
    try:
        pipeline = [
            {"$group": {
                "_id": "$test_id",
                "attempts": {"$sum": 1},
                "avg_score": {"$avg": "$score"},
                "completed": {"$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}}
            }}
        ]
        
        results = await db.test_results.aggregate(pipeline).to_list(10000)
        
        performance = []
        for r in results:
            test = await db.tests.find_one({"id": r["_id"]})
            if test:
                completion_rate = (r["completed"] / r["attempts"] * 100) if r["attempts"] > 0 else 0
                performance.append({
                    "test_id": r["_id"],
                    "test_name": test.get("title", "Unknown"),
                    "attempts": r["attempts"],
                    "avg_score": round(r["avg_score"], 2) if r["avg_score"] else 0,
                    "completion_rate": round(completion_rate, 2)
                })
        
        return sorted(performance, key=lambda x: x["attempts"], reverse=True)
    except Exception as e:
        logger.error(f"Test performance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/analytics/payment-methods")
async def get_payment_methods(admin: User = Depends(require_admin)):
    """Get payment method breakdown"""
    try:
        # Note: This would require storing payment method info in purchases
        # For now, return mock data structure
        pipeline = [
            {"$group": {
                "_id": "$payment_method",
                "count": {"$sum": 1},
                "revenue": {"$sum": "$amount"}
            }}
        ]
        
        results = await db.purchases.aggregate(pipeline).to_list(10000)
        
        if not results or all(r["_id"] is None for r in results):
            # Return default structure if no payment method data
            return {
                "methods": [
                    {"method": "Cards", "count": 0, "revenue": 0},
                    {"method": "UPI", "count": 0, "revenue": 0},
                    {"method": "Net Banking", "count": 0, "revenue": 0},
                    {"method": "Wallets", "count": 0, "revenue": 0}
                ]
            }
        
        return {
            "methods": [
                {
                    "method": r["_id"] or "Not specified",
                    "count": r["count"],
                    "revenue": round(r["revenue"], 2)
                }
                for r in results
            ]
        }
    except Exception as e:
        logger.error(f"Payment methods error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/admin/analytics/recent-purchases")
async def get_recent_purchases(
    limit: int = 10,
    admin: User = Depends(require_admin)
):
    """Get recent purchase transactions"""
    try:
        purchases = await db.purchases.find({}).sort("created_at", -1).limit(limit).to_list(limit)
        
        result = []
        for p in purchases:
            user = await db.users.find_one({"id": p.get("user_id")})
            test = await db.tests.find_one({"id": p.get("test_id")})
            
            result.append({
                "purchase_id": p.get("id"),
                "student_name": user.get("name", "Unknown") if user else "Unknown",
                "student_email": user.get("email", "Unknown") if user else "Unknown",
                "test_name": test.get("title", "Unknown") if test else "Unknown",
                "amount": p.get("amount", 0),
                "payment_id": p.get("payment_id", "N/A"),
                "created_at": p.get("created_at").isoformat() if p.get("created_at") else None
            })
        
        return result
    except Exception as e:
        logger.error(f"Recent purchases error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== BASIC ROUTES =====
@api_router.get("/")
async def root():
    return {"message": "Test Platform API"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Razorpay configuration
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')
RAZORPAY_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET')

# Initialize Razorpay client
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
else:
    razorpay_client = None
    logger.warning("Razorpay credentials not configured")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()