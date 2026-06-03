# ============================================================
# VERITAS MICROFINANCE BANK - Transaction Model
# OOP: Inheritance (Base), Encapsulation
# ============================================================
from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, Text,
    ForeignKey, Sequence, CheckConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Transaction(Base):
    """
    Represents a single ledger entry (credit or debit).
    OOP Principles:
      - Inheritance: extends Base
      - Encapsulation: financial data as managed state
    """
    __tablename__ = "TRANSACTIONS"

    # Primary key
    transaction_id   = Column(Integer, Sequence("SEQ_TRANSACTION_ID"), primary_key=True)
    account_id       = Column(Integer, ForeignKey("ACCOUNTS.account_id"), nullable=False, index=True)

    # Transaction details
    transaction_ref  = Column(String(30), unique=True, nullable=False, index=True)
    transaction_type = Column(String(10), nullable=False)   # CREDIT / DEBIT
    amount           = Column(Numeric(18, 2), nullable=False)
    balance_before   = Column(Numeric(18, 2), nullable=False)
    balance_after    = Column(Numeric(18, 2), nullable=False)

    # Metadata
    description      = Column(String(255), nullable=True)
    channel          = Column(String(20), default="MOBILE")  # MOBILE / WEB / ATM / POS / USSD
    status           = Column(String(20), default="SUCCESS")  # SUCCESS / FAILED / PENDING
    ip_address       = Column(String(50), nullable=True)

    # Timestamps
    transaction_date = Column(DateTime, default=datetime.utcnow)
    created_at       = Column(DateTime, default=datetime.utcnow)

    # ── Table constraints ────────────────────
    __table_args__ = (
        CheckConstraint("transaction_type IN ('CREDIT','DEBIT')", name="CK_TXN_TYPE"),
        CheckConstraint("status IN ('SUCCESS','FAILED','PENDING')", name="CK_TXN_STATUS"),
    )

    # ── Relationships ────────────────────────
    account = relationship("Account", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.transaction_ref} | {self.transaction_type} | {self.amount}>"
