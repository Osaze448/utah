# ============================================================
# VERITAS MICROFINANCE BANK - Account Model
# OOP: Inheritance (Base), Encapsulation, Composition (FK)
# ============================================================
from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, Date,
    ForeignKey, Sequence, CheckConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from app.core.database import Base


class Account(Base):
    """
    Represents a bank account (Savings, Current, Fixed Deposit).
    OOP Principles:
      - Inheritance: extends Base
      - Encapsulation: balance and limits as private state
      - Composition: belongs to Customer, owns Transactions
    """
    __tablename__ = "ACCOUNTS"

    # Primary key
    account_id      = Column(Integer, Sequence("SEQ_ACCOUNT_ID"), primary_key=True)
    customer_id     = Column(Integer, ForeignKey("CUSTOMERS.customer_id"), nullable=False, index=True)

    # Account details
    account_number  = Column(String(10), unique=True, nullable=False, index=True)
    account_name    = Column(String(200), nullable=False)
    account_type    = Column(String(20), nullable=False)  # SAVINGS / CURRENT / FIXED_DEPOSIT

    # Balances
    balance         = Column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    ledger_balance  = Column(Numeric(18, 2), default=Decimal("0.00"), nullable=False)
    currency        = Column(String(3), default="NGN")

    # Status & limits
    status          = Column(String(20), default="ACTIVE")  # ACTIVE / FROZEN / DORMANT / CLOSED
    interest_rate   = Column(Numeric(5, 2), default=Decimal("4.50"))
    daily_limit     = Column(Numeric(18, 2), default=Decimal("1000000.00"))
    overdraft_limit = Column(Numeric(18, 2), default=Decimal("0.00"))
    tier            = Column(Integer, default=1)

    # Branch
    branch_id       = Column(Integer, default=1)

    # Timestamps
    opened_date      = Column(Date, default=date.today)
    last_transaction = Column(DateTime, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Table constraints ────────────────────
    __table_args__ = (
        CheckConstraint("account_type IN ('SAVINGS','CURRENT','FIXED_DEPOSIT')", name="CK_ACCOUNT_TYPE"),
        CheckConstraint("status IN ('ACTIVE','FROZEN','DORMANT','CLOSED')", name="CK_ACCOUNT_STATUS"),
    )

    # ── Relationships (Composition) ──────────
    customer     = relationship("Customer", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", lazy="dynamic")

    def __repr__(self):
        return f"<Account {self.account_number} | {self.account_type} | {self.status}>"
