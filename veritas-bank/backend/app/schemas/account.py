from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import date

class CreateAccountRequest(BaseModel):
    account_type: str = Field(..., pattern=r"^(SAVINGS|CURRENT|FIXED_DEPOSIT)$")
    branch_id: Optional[int] = 1
 
class AccountResponse(BaseModel):
    account_id: int
    account_number: str
    account_type: str
    account_name: str
    balance: Decimal
    ledger_balance: Decimal
    currency: str
    status: str
    interest_rate: Decimal
    daily_limit: Decimal
    tier: int
    opened_date: date
 
    class Config:
        from_attributes = True
 
class AccountBalanceResponse(BaseModel):
    account_number: str
    account_name: str
    balance: Decimal
    ledger_balance: Decimal
    currency: str
    status: str
 
class FreezeAccountRequest(BaseModel):
    account_number: str
    action: str = Field(..., pattern=r"^(FREEZE|UNFREEZE)$")
    reason: str = Field(..., min_length=10)
 