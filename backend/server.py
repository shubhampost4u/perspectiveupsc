from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
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
import re

# Twilio imports
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️ Twilio not available - OTP features will be disabled")

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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Twilio setup
if TWILIO_AVAILABLE:
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN') 
    TWILIO_VERIFY_SERVICE = os.environ.get('TWILIO_VERIFY_SERVICE')
    
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    else:
        twilio_client = None
        print("⚠️ Twilio credentials not configured")
else:
    twilio_client = None

# Create the main app without a prefix
app = FastAPI(title="Test Platform API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ===== MODELS =====
class UserRole(str):
    ADMIN = "admin"
    STUDENT = "student"

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    name: str
    role: str = UserRole.STUDENT

class UserCreate(UserBase):
    password: Optional[str] = None
    # Either email+password OR mobile (for OTP) is required

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class MobileLoginRequest(BaseModel):
    mobile: str

class OTPVerifyRequest(BaseModel):
    mobile: str
    otp: str
    name: Optional[str] = None  # For registration

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    password: Optional[str] = None  # Optional for mobile-only users
    mobile_verified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class UserResponse(BaseModel):
    id: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    name: str
    role: str
    is_active: bool
    mobile_verified: Optional[bool] = False

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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TestResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    test_id: str
    answers: List[int]  # Student's selected options
    score: int
    total_questions: int
    time_taken_minutes: int
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ===== UTILITY FUNCTIONS =====
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def format_mobile_number(mobile: str) -> str:
    """Format mobile number to E.164 format for India"""
    # Remove all non-digit characters
    mobile = re.sub(r'\D', '', mobile)
    
    # If it starts with 91, assume it's already with country code
    if mobile.startswith('91') and len(mobile) == 12:
        return f"+{mobile}"
    
    # If it's 10 digits, assume it's Indian number without country code
    if len(mobile) == 10:
        return f"+91{mobile}"
    
    # If it already starts with +, return as is
    if mobile.startswith('+'):
        return mobile
        
    raise ValueError("Invalid mobile number format")

def validate_indian_mobile(mobile: str) -> bool:
    """Validate Indian mobile number"""
    try:
        formatted = format_mobile_number(mobile)
        # Indian mobile numbers: +91 followed by 10 digits starting with 6,7,8,9
        pattern = r'^\+91[6-9]\d{9}$'
        return bool(re.match(pattern, formatted))
    except ValueError:
        return False

async def send_otp_sms(mobile: str) -> bool:
    """Send OTP via Twilio SMS"""
    if not twilio_client or not TWILIO_VERIFY_SERVICE:
        logger.warning("Twilio not configured, OTP sending disabled")
        return False
    
    try:
        formatted_mobile = format_mobile_number(mobile)
        verification = twilio_client.verify.services(TWILIO_VERIFY_SERVICE).verifications.create(
            to=formatted_mobile,
            channel='sms'
        )
        logger.info(f"OTP sent to {formatted_mobile}, status: {verification.status}")
        return verification.status == 'pending'
    except Exception as e:
        logger.error(f"Failed to send OTP to {mobile}: {str(e)}")
        return False

async def verify_otp_sms(mobile: str, otp: str) -> bool:
    """Verify OTP via Twilio"""
    if not twilio_client or not TWILIO_VERIFY_SERVICE:
        logger.warning("Twilio not configured, OTP verification disabled")
        return False
    
    try:
        formatted_mobile = format_mobile_number(mobile)
        check = twilio_client.verify.services(TWILIO_VERIFY_SERVICE).verification_checks.create(
            to=formatted_mobile,
            code=otp
        )
        logger.info(f"OTP verification for {formatted_mobile}: {check.status}")
        return check.status == 'approved'
    except Exception as e:
        logger.error(f"Failed to verify OTP for {mobile}: {str(e)}")
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
    
    # Try to find user by email first, then by mobile
    user = await db.users.find_one({"email": token_subject})
    if not user:
        user = await db.users.find_one({"mobile": token_subject})
    
    if user is None:
        raise credentials_exception
    return User(**user)

async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# ===== AUTHENTICATION ROUTES =====
@api_router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    # Validate that either email+password OR mobile is provided
    if user.email and user.password:
        # Email registration
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
    
    elif user.mobile:
        # Mobile registration - requires OTP verification first
        if not validate_indian_mobile(user.mobile):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Indian mobile number"
            )
        
        formatted_mobile = format_mobile_number(user.mobile)
        existing_user = await db.users.find_one({"mobile": formatted_mobile})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already registered"
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile registration requires OTP verification. Use /send-otp first."
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either email+password or mobile number is required"
        )

@api_router.post("/send-otp")
async def send_otp(request: MobileLoginRequest):
    """Send OTP to mobile number for registration or login"""
    if not validate_indian_mobile(request.mobile):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Indian mobile number. Use format: +91XXXXXXXXXX or 10-digit number"
        )
    
    formatted_mobile = format_mobile_number(request.mobile)
    
    # Send OTP via Twilio
    success = await send_otp_sms(formatted_mobile)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP. Please try again."
        )
    
    return {"message": "OTP sent successfully", "mobile": formatted_mobile}

@api_router.post("/verify-otp-register", response_model=UserResponse) 
async def verify_otp_and_register(request: OTPVerifyRequest):
    """Verify OTP and register new user with mobile number"""
    if not request.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name is required for registration"
        )
    
    if not validate_indian_mobile(request.mobile):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mobile number"
        )
    
    formatted_mobile = format_mobile_number(request.mobile)
    
    # Check if mobile already registered
    existing_user = await db.users.find_one({"mobile": formatted_mobile})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered. Use login instead."
        )
    
    # Verify OTP
    otp_valid = await verify_otp_sms(formatted_mobile, request.otp)
    if not otp_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Create new user
    user_data = {
        "name": request.name,
        "mobile": formatted_mobile,
        "role": UserRole.STUDENT,
        "mobile_verified": True,
        "email": None,
        "password": None
    }
    
    new_user = User(**user_data)
    await db.users.insert_one(new_user.dict())
    
    return UserResponse(**new_user.dict())

@api_router.post("/verify-otp-login", response_model=Token)
async def verify_otp_and_login(request: OTPVerifyRequest):
    """Verify OTP and login existing user"""
    if not validate_indian_mobile(request.mobile):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mobile number"
        )
    
    formatted_mobile = format_mobile_number(request.mobile)
    
    # Find existing user
    user = await db.users.find_one({"mobile": formatted_mobile})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mobile number not registered. Please register first."
        )
    
    # Verify OTP
    otp_valid = await verify_otp_sms(formatted_mobile, request.otp)
    if not otp_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Update mobile verification status
    await db.users.update_one(
        {"mobile": formatted_mobile},
        {"$set": {"mobile_verified": True}}
    )
    
    # Generate JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Use mobile as subject since email might be None
    token_subject = user.get("email") or user.get("mobile")
    access_token = create_access_token(
        data={"sub": token_subject}, expires_delta=access_token_expires
    )
    
    # Create UserResponse directly from database fields
    user_response = UserResponse(
        id=user["id"],
        email=user.get("email"),
        mobile=user.get("mobile"),
        name=user["name"],
        role=user["role"],
        is_active=user["is_active"],
        mobile_verified=user.get("mobile_verified", False)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

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

@api_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

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

@api_router.get("/admin/students", response_model=List[UserResponse])
async def get_students(admin: User = Depends(require_admin)):
    students = await db.users.find({"role": UserRole.STUDENT}).to_list(1000)
    return [UserResponse(**student) for student in students]

# ===== STUDENT ROUTES =====
@api_router.get("/tests", response_model=List[TestResponse])
async def get_available_tests():
    tests = await db.tests.find({"is_active": True}).to_list(1000)
    return [TestResponse(**test, questions_count=len(test["questions"])) for test in tests]

@api_router.post("/tests/{test_id}/purchase")
async def purchase_test(test_id: str, current_user: User = Depends(get_current_user)):
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
    
    # For MVP, we'll mark as completed without actual payment
    # In production, integrate with Stripe here
    purchase = Purchase(
        student_id=current_user.id,
        test_id=test_id,
        amount=test["price"],
        status="completed"
    )
    
    await db.purchases.insert_one(purchase.dict())
    return {"message": "Test purchased successfully"}

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
                "test_title": test["title"],
                "score": result["score"],
                "total_questions": result["total_questions"],
                "percentage": round((result["score"] / result["total_questions"]) * 100, 2),
                "completed_at": result["completed_at"]
            })
    
    return enriched_results

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()