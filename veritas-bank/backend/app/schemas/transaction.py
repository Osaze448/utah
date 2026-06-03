from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class DepositRequest(BaseModel):
    account_number: str = Field(..., min_length=10, max_length=10)
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = "Cash Deposit"
    channel: str = "MOBILE"
 
class WithdrawRequest(BaseModel):
    account_number: str = Field(..., min_length=10, max_length=10)
    amount: Decimal = Field(..., gt=0)
    pin: str = Field(..., min_length=4, max_length=6)
    description: Optional[str] = "Cash Withdrawal"
    channel: str = "MOBILE"
 
class TransferRequest(BaseModel):
    source_account: str = Field(..., min_length=10, max_length=10)
    destination_account: str = Field(..., min_length=10, max_length=10)
    amount: Decimal = Field(..., gt=0)
    narration: str = Field(..., min_length=3, max_length=100)
    transfer_type: str = Field(default="INTRABANK", pattern=r"^(INTRABANK|INTERBANK)$")
    pin: str = Field(..., min_length=4, max_length=6)
 
    @validator("destination_account")
    def not_same_account(cls, v, values):
        if "source_account" in values and v == values["source_account"]:
            raise ValueError("Source and destination accounts cannot be the same.")
        return v
 
class TransactionResponse(BaseModel):
    transaction_id: int
    transaction_ref: str
    transaction_type: str
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    description: Optional[str]
    channel: str
    status: str
    transaction_date: datetime
 
    class Config:
        from_attributes = True
 
class TransactionHistoryResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int
 
class TransferResponse(BaseModel):
    transfer_ref: str
    amount: Decimal
    fee: Decimal
    dest_account_name: str
    dest_account_no: str
    status: str
    narration: Optional[str]
    created_at: datetime
 
    class Config:
        from_attributes = True