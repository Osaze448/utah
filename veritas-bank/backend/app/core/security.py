# ============================================================
# VERITAS MICROFINANCE BANK - Security Module
# JWT Authentication + Password Hashing + RBAC
# ============================================================
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
import secrets
import hashlib
 
# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
 
# OAuth2 bearer token scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
 
 
# ─────────────────────────────────────────────
# Password Utilities
# ─────────────────────────────────────────────
class PasswordManager:
    """Encapsulates all password hashing and verification logic."""
 
    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Hash a plaintext password using bcrypt."""
        return pwd_context.hash(plain_password)
 
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against its bcrypt hash."""
        return pwd_context.verify(plain_password, hashed_password)
 
    @staticmethod
    def hash_pin(pin: str) -> str:
        """Hash a 4-6 digit PIN using SHA-256 + salt."""
        salt = secrets.token_hex(16)
        pin_hash = hashlib.sha256(f"{salt}{pin}".encode()).hexdigest()
        return f"{salt}:{pin_hash}"
 
    @staticmethod
    def verify_pin(plain_pin: str, stored_hash: str) -> bool:
        """Verify a PIN against its stored hash."""
        try:
            salt, pin_hash = stored_hash.split(":")
            return hashlib.sha256(f"{salt}{plain_pin}".encode()).hexdigest() == pin_hash
        except Exception:
            return False
 
 
# ─────────────────────────────────────────────
# JWT Token Utilities
# ─────────────────────────────────────────────
class TokenManager:
    """Handles JWT creation and validation."""
 
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
 
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
 
    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
 
 
# ─────────────────────────────────────────────
# Role-Based Access Control
# ─────────────────────────────────────────────
class Role:
    CUSTOMER     = "CUSTOMER"
    TELLER       = "TELLER"
    MANAGER      = "MANAGER"
    ADMIN        = "ADMIN"
    SUPER_ADMIN  = "SUPER_ADMIN"
    AUDITOR      = "AUDITOR"
 
    STAFF_ROLES = {TELLER, MANAGER, ADMIN, SUPER_ADMIN, AUDITOR}
    ADMIN_ROLES = {ADMIN, SUPER_ADMIN}
 
 
# ─────────────────────────────────────────────
# FastAPI Dependency: Get Current User
# ─────────────────────────────────────────────
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Extract and validate the current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = TokenManager.decode_token(token)
    user_id: str = payload.get("sub")
    user_type: str = payload.get("user_type")  # "customer" or "staff"
 
    if user_id is None or user_type is None:
        raise credentials_exception
 
    # Import here to avoid circular imports
    if user_type == "customer":
        from app.models.customer import Customer
        user = db.query(Customer).filter(Customer.customer_id == int(user_id)).first()
    else:
        from app.models.bank_staff import BankStaff
        user = db.query(BankStaff).filter(BankStaff.staff_id == int(user_id)).first()
 
    if user is None:
        raise credentials_exception
    if not user.is_active or user.is_active == 'N':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive.")
 
    return {"user": user, "user_type": user_type, "role": getattr(user, "role", Role.CUSTOMER)}
 
 
async def get_current_customer(current=Depends(get_current_user)):
    if current["user_type"] != "customer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer access required.")
    return current["user"]
 
 
async def get_current_staff(current=Depends(get_current_user)):
    if current["user_type"] != "staff":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff access required.")
    return current["user"]
 
 
async def get_current_admin(current=Depends(get_current_user)):
    if current["role"] not in Role.ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return current["user"]
 
 
# Instantiate for direct use
password_manager = PasswordManager()
token_manager = TokenManager()