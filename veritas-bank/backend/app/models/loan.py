# ============================================================
# VERITAS MICROFINANCE BANK - Loan Model
# OOP: Inheritance (Base), Encapsulation
# ============================================================
from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, Date,
    ForeignKey, Sequence, CheckConstraint
)
from datetime import datetime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Loan(Base):
    """
    Represents a loan application / active loan.
    OOP Principles:
      - Inheritance: extends Base
      - Encapsulation: loan financials as internal state
    """
    __tablename__ = "LOANS"

    # Primary key
    loan_id            = Column(Integer, Sequence("SEQ_LOAN_ID"), primary_key=True)

    # Foreign keys
    account_id         = Column(Integer, ForeignKey("ACCOUNTS.account_id"), nullable=False)
    customer_id        = Column(Integer, ForeignKey("CUSTOMERS.customer_id"), nullable=False, index=True)

    # Loan details
    loan_ref           = Column(String(30), unique=True, nullable=False, index=True)
    loan_type          = Column(String(20), nullable=False)  # PERSONAL / BUSINESS / MICRO / AUTO / MORTGAGE
    principal_amount   = Column(Numeric(18, 2), nullable=False)
    outstanding_amount = Column(Numeric(18, 2), nullable=False)
    interest_rate      = Column(Numeric(5, 2), nullable=False)
    tenure_months      = Column(Integer, nullable=False)
    monthly_repayment  = Column(Numeric(18, 2), nullable=False)

    # Status
    status             = Column(String(20), default="PENDING")
    # PENDING / APPROVED / DISBURSED / ACTIVE / COMPLETED / REJECTED / DEFAULTED

    # Approval
    approved_by        = Column(Integer, nullable=True)   # staff_id
    approved_at        = Column(DateTime, nullable=True)
    disbursed_at       = Column(DateTime, nullable=True)
    due_date           = Column(Date, nullable=True)

    # Timestamps
    created_at         = Column(DateTime, default=datetime.utcnow)
    updated_at         = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Table constraints ────────────────────
    __table_args__ = (
        CheckConstraint(
            "loan_type IN ('PERSONAL','BUSINESS','MICRO','AUTO','MORTGAGE')",
            name="CK_LOAN_TYPE"
        ),
        CheckConstraint(
            "status IN ('PENDING','APPROVED','DISBURSED','ACTIVE','COMPLETED','REJECTED','DEFAULTED')",
            name="CK_LOAN_STATUS"
        ),
    )

    # ── Relationships ────────────────────────
    customer = relationship("Customer", back_populates="loans")

    def __repr__(self):
        return f"<Loan {self.loan_ref} | {self.loan_type} | {self.principal_amount} | {self.status}>"
