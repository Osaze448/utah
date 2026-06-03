# ============================================================
# VERITAS MICROFINANCE BANK - Bank Staff Model
# OOP: Inheritance (Base), Encapsulation
# ============================================================
from sqlalchemy import (
    Column, Integer, String, DateTime,
    Sequence
)
from datetime import datetime
from app.core.database import Base


class BankStaff(Base):
    """
    Represents bank employees (tellers, managers, admins).
    OOP Principles:
      - Inheritance: extends Base
      - Encapsulation: credentials and role as managed state
    """
    __tablename__ = "BANK_STAFF"

    # Primary key
    staff_id       = Column(Integer, Sequence("SEQ_STAFF_ID"), primary_key=True)

    # Identity
    employee_code  = Column(String(20), unique=True, nullable=False)
    first_name     = Column(String(100), nullable=False)
    last_name      = Column(String(100), nullable=False)
    email          = Column(String(150), unique=True, nullable=False, index=True)

    # Security
    password_hash  = Column(String(255), nullable=False)
    role           = Column(String(20), nullable=False, default="TELLER")
    # TELLER / MANAGER / ADMIN / SUPER_ADMIN / AUDITOR

    # Branch
    branch_id      = Column(Integer, default=1)

    # Status
    is_active      = Column(String(1), default="Y")

    # Timestamps
    last_login     = Column(DateTime, nullable=True)
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<BankStaff {self.employee_code} | {self.role}>"
