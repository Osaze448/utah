from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date, datetime
import re

class CustomerRegisterRequest(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    middle_name: Optional[str] = None
    email: EmailStr
    phone: str = Field(..., pattern=r"^(\+234|0)[789][01]\d{8}$")
    date_of_birth: date
    gender: str = Field(..., pattern=r"^[MFO]$")
    address: str = Field(..., min_length=10)
    city: str
    state: str
    password: str = Field(..., min_length=8)
    bvn: Optional[str] = Field(None, min_length=11, max_length=11)
 
    @validator("date_of_birth")
    def must_be_adult(cls, v):
        from datetime import date
        age = (date.today() - v).days / 365
        if age < 18:
            raise ValueError("Customer must be at least 18 years old.")
        return v
 
    @validator("password")
    def strong_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character.")
        return v
 
class CustomerResponse(BaseModel):
    customer_id: int
    customer_code: str
    first_name: str
    last_name: str
    email: str
    phone: str
    kyc_level: int
    kyc_verified: str
    is_active: str
    created_at: datetime
 
    class Config:
        from_attributes = True
 
class CustomerProfileResponse(CustomerResponse):
    middle_name: Optional[str]
    date_of_birth: date
    gender: str
    address: str
    city: str
    state: str
    country: str
    profile_photo: Optional[str]
    last_login: Optional[datetime]
 
class UpdateProfileRequest(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    phone: Optional[str] = None