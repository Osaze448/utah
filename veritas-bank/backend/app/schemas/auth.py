# ============================================================
# VERITAS MICROFINANCE BANK - Pydantic Schemas
# Request/Response validation for all API endpoints
# ============================================================
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
import re
 
 
# ─────────────────────────────────────────────
# AUTH SCHEMAS
# ─────────────────────────────────────────────
class CustomerLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
 
class StaffLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
 
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_type: str
 
class RefreshTokenRequest(BaseModel):
    refresh_token: str
 
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
 
    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Passwords do not match.")
        return v
 
class SetPinRequest(BaseModel):
    pin: str = Field(..., min_length=4, max_length=6, pattern=r"^\d+$")
    confirm_pin: str
 
    @validator("confirm_pin")
    def pins_match(cls, v, values):
        if "pin" in values and v != values["pin"]:
            raise ValueError("PINs do not match.")
        return v