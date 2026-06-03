# ============================================================
# VERITAS MICROFINANCE BANK - Loan Pydantic Schemas
# Request/Response validation for Loan APIs
# ============================================================
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class LoanApplicationRequest(BaseModel):
    account_number: str = Field(..., min_length=10, max_length=10)
    loan_type: str = Field(..., pattern=r"^(PERSONAL|BUSINESS|MORTGAGE|STUDENT)$")
    principal_amount: Decimal = Field(..., gt=1000)
    tenure_months: int = Field(..., gt=0, le=120)


class LoanResponse(BaseModel):
    loan_id: int
    loan_ref: str
    account_id: int
    customer_id: int
    loan_type: str
    principal_amount: Decimal
    outstanding_amount: Decimal
    interest_rate: Decimal
    tenure_months: int
    monthly_repayment: Decimal
    status: str
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    disbursed_at: Optional[datetime] = None
    due_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoanListResponse(BaseModel):
    loans: List[LoanResponse]
    total: int
