# ============================================================
# VERITAS MICROFINANCE BANK - Admin Pydantic Schemas
# Request/Response validation for Administrative APIs
# ============================================================
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class DashboardStatsResponse(BaseModel):
    total_customers: int
    total_accounts: int
    total_deposits: Decimal
    total_loans_disbursed: Decimal
    total_active_loans: Decimal
    pending_loan_applications: int


class StaffCreateRequest(BaseModel):
    employee_code: str = Field(..., min_length=4, max_length=20)
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(..., pattern=r"^(TELLER|MANAGER|ADMIN)$")
    branch_id: Optional[int] = 1


class StaffResponse(BaseModel):
    staff_id: int
    employee_code: str
    first_name: str
    last_name: str
    email: str
    role: str
    is_active: str
    created_at: datetime

    class Config:
        from_attributes = True
