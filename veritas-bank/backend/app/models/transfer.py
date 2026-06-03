# ============================================================
# VERITAS MICROFINANCE BANK - Transfer Model
# OOP: Inheritance (Base), Encapsulation
# ============================================================
from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime,
    ForeignKey, Sequence, CheckConstraint
)
from datetime import datetime
from app.core.database import Base


class Transfer(Base):
    """
    Represents a fund transfer between accounts.
    OOP Principles:
      - Inheritance: extends Base
      - Encapsulation: transfer details as managed state
    """
    __tablename__ = "TRANSFERS"

    # Primary key
    transfer_id       = Column(Integer, Sequence("SEQ_TRANSFER_ID"), primary_key=True)

    # Reference
    transfer_ref      = Column(String(30), unique=True, nullable=False, index=True)

    # Source & Destination
    source_account_id = Column(Integer, ForeignKey("ACCOUNTS.account_id"), nullable=False)
    dest_account_id   = Column(Integer, ForeignKey("ACCOUNTS.account_id"), nullable=True)
    dest_account_no   = Column(String(20), nullable=False)
    dest_bank_name    = Column(String(100), nullable=True)
    dest_account_name = Column(String(200), nullable=True)

    # Financial
    amount            = Column(Numeric(18, 2), nullable=False)
    fee               = Column(Numeric(18, 2), default=0.00)
    narration         = Column(String(255), nullable=True)

    # Classification
    transfer_type     = Column(String(20), nullable=False)  # INTRABANK / INTERBANK
    status            = Column(String(20), default="PENDING")  # PENDING / SUCCESS / FAILED

    # Timestamps
    completed_at      = Column(DateTime, nullable=True)
    created_at        = Column(DateTime, default=datetime.utcnow)

    # ── Table constraints ────────────────────
    __table_args__ = (
        CheckConstraint("transfer_type IN ('INTRABANK','INTERBANK')", name="CK_TRANSFER_TYPE"),
        CheckConstraint("status IN ('PENDING','SUCCESS','FAILED','REVERSED')", name="CK_TRANSFER_STATUS"),
    )

    def __repr__(self):
        return f"<Transfer {self.transfer_ref} | {self.amount} | {self.status}>"
