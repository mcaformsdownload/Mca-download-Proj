from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from emailer import send_otp_email
# Load from .env
from dotenv import load_dotenv
from redis_client import redis_client
import random
from emailer import send_email
load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

auth_router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# Pydantic Request Models
# -----------------------------
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# -----------------------------
# Utility Functions
# -----------------------------
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# -----------------------------
# Auth Routes
# -----------------------------

@auth_router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=req.email, hashed_password=hash_password(req.password))
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@auth_router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

class OTPRequestModel(BaseModel):
    email: EmailStr

@auth_router.post("/send-otp")
def send_otp(req: OTPRequestModel):
    otp = str(random.randint(100000, 999999))

    # Save OTP to Redis with 10 min expiry
    redis_client.setex(f"otp:{req.email}", 600, otp)

    send_otp_email(req.email, otp)
    return {"message": "OTP sent"}
class OTPVerifyModel(BaseModel):
    email: EmailStr
    otp: str
    password: str

@auth_router.post("/verify-otp")
def verify_otp(req: OTPVerifyModel, db: Session = Depends(get_db)):
    saved_otp = redis_client.get(f"otp:{req.email}")

    if not saved_otp or saved_otp != req.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = db.query(User).filter(User.email == req.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(req.password)
    new_user = User(email=req.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()

    # Delete OTP after success
    redis_client.delete(f"otp:{req.email}")

    return {"message": "User registered successfully"}
# -----------------------25/07/25---------------------

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

@auth_router.post("/forgot-password/send-otp")
def send_otp_for_reset(req: ForgotPasswordRequest):
    otp = str(random.randint(100000, 999999))

    # Save OTP in Redis with expiry
    redis_client.setex(f"forgot_otp:{req.email}", 300, otp)  # 5 mins expiry

    # Send OTP via email
    send_email(
    to_email=req.email,
    subject="Reset Password OTP",
    body=f"Your OTP for password reset is: {otp}"
)

    return {"message": "OTP sent successfully"}

class ResetPasswordOtpRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

@auth_router.post("/forgot-password/reset")
def reset_password_otp(req: ResetPasswordOtpRequest, db: Session = Depends(get_db)):
    stored_otp = redis_client.get(f"forgot_otp:{req.email}")

    if not stored_otp or stored_otp != req.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(req.new_password)
    db.commit()

    # Delete OTP from Redis
    redis_client.delete(f"forgot_otp:{req.email}")

    return {"message": "Password reset successfully"}

# ------------------------------------------------------