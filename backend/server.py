from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File, Request
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
    reset_token: str
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

# ===== UTILITY FUNCTIONS =====
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def send_reset_email(email: str, reset_token: str) -> bool:
    """Send password reset email"""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.warning("SMTP not configured, password reset email disabled")
        # For demo purposes, just log the reset token
        logger.info(f"Password reset token for {email}: {reset_token}")
        print(f"🔐 Password reset token for {email}: {reset_token}")
        return True
    
    try:
        # Create email message
        subject = "Password Reset - Perspective UPSC"
        body = f"""
        Hello,
        
        You have requested a password reset for your Perspective UPSC account.
        
        Your password reset token is: {reset_token}
        
        Please use this token to reset your password. This token will expire in 1 hour.
        
        If you didn't request this reset, please ignore this email.
        
        Best regards,
        Perspective UPSC Team
        """
        
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        if SMTP_PORT == 465:
            # Use SSL for port 465
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # Use TLS for port 587
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
        
        logger.info(f"Password reset email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send reset email to {email}: {str(e)}")
        # For demo, still log the token even if email fails
        logger.info(f"Password reset token for {email}: {reset_token}")
        print(f"🔐 Password reset token for {email}: {reset_token}")
        return True  # Return True for demo purposes

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
    """Send password reset email to user"""
    # Always return the same message for security (don't reveal if email exists)
    user = await db.users.find_one({"email": request.email})
    
    if user and user["role"] == UserRole.STUDENT:
        # Generate secure reset token
        reset_token = secrets.token_urlsafe(32)
        expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Store reset token in database
        await db.password_resets.insert_one({
            "email": request.email,
            "token": reset_token,
            "expires_at": expiry,
            "used": False
        })
        
        # Send password reset email
        await send_reset_email(request.email, reset_token)
    
    return {"message": "If the email exists, a password reset link has been sent"}

@api_router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset user password using reset token"""
    # Find valid reset token
    reset_record = await db.password_resets.find_one({
        "email": request.email,
        "token": request.reset_token,
        "used": False,
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
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
    
    return {"message": "Password reset successfully"}

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
            "Maximum 100 questions per upload",
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
        
        if len(df) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 100 questions allowed per upload"
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