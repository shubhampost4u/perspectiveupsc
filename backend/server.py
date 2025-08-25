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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets

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

# Email setup for password reset
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
FROM_EMAIL = os.environ.get('FROM_EMAIL', SMTP_USERNAME)

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
    reset_token: str
    new_password: str

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    password: str  # Add password field for database storage
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

@api_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

@api_router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset token to user's email"""
    user = await db.users.find_one({"email": request.email})
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate reset token (in production, use a more secure method)
    reset_token = secrets.token_urlsafe(32)
    expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    
    # Store reset token in database (you might want a separate collection for this)
    await db.password_resets.insert_one({
        "email": request.email,
        "token": reset_token,
        "expiry": expiry,
        "used": False
    })
    
    # In production, send email with reset link
    logger.info(f"Password reset token for {request.email}: {reset_token}")
    print(f"🔑 Password reset token for {request.email}: {reset_token}")
    
    return {"message": "If the email exists, a password reset link has been sent"}

@api_router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password using reset token"""
    # Find valid reset token
    reset_record = await db.password_resets.find_one({
        "email": request.email,
        "token": request.reset_token,
        "used": False
    })
    
    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token has expired
    if datetime.now(timezone.utc) > reset_record["expiry"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Update user password
    hashed_password = get_password_hash(request.new_password)
    await db.users.update_one(
        {"email": request.email},
        {"$set": {"password": hashed_password}}
    )
    
    # Mark reset token as used
    await db.password_resets.update_one(
        {"_id": reset_record["_id"]},
        {"$set": {"used": True}}
    )
    
    return {"message": "Password has been reset successfully"}

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