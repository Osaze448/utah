# ============================================================
# VERITAS MICROFINANCE BANK - Customer Model
# OOP: Inheritance (Base), Encapsulation (column state)
# ============================================================
from sqlalchemy import (
    Column, Integer, String, Date, DateTime, Text,
    Sequence, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Customer(Base):
    """
    Represents a bank customer.
    OOP Principles:
      - Inheritance: extends SQLAlchemy Base
      - Encapsulation: internal state managed via columns
      - Composition: owns a collection of Account objects
    """
    __tablename__ = "CUSTOMERS"

    # Primary key
    customer_id    = Column(Integer, Sequence("SEQ_CUSTOMER_ID"), primary_key=True)
    customer_code  = Column(String(20), unique=True, nullable=False)

    # Personal info
    first_name     = Column(String(100), nullable=False)
    last_name      = Column(String(100), nullable=False)
    middle_name    = Column(String(100), nullable=True)
    email          = Column(String(150), unique=True, nullable=False, index=True)
    phone          = Column(String(20), unique=True, nullable=False, index=True)
    date_of_birth  = Column(Date, nullable=False)
    gender         = Column(String(1), nullable=False)   # M / F / O

    # Address
    address        = Column(Text, nullable=False)
    city           = Column(String(100), nullable=False)
    state          = Column(String(100), nullable=False)
    country        = Column(String(100), default="Nigeria")

    # Identity
    bvn            = Column(String(11), nullable=True, unique=True)
    profile_photo  = Column(String(500), nullable=True)

    # Security
    password_hash  = Column(String(255), nullable=False)
    pin_hash       = Column(String(255), nullable=True)
    failed_attempts = Column(Integer, default=0)
    locked_until   = Column(DateTime, nullable=True)

    # KYC
    kyc_level      = Column(Integer, default=1)
    kyc_verified   = Column(String(1), default="N")   # Y / N

    # Status
    is_active      = Column(String(1), default="Y")
    is_blacklisted = Column(String(1), default="N")

    # Timestamps
    last_login     = Column(DateTime, nullable=True)
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships (Composition) ──────────
    accounts       = relationship("Account", back_populates="customer", lazy="dynamic")
    loans          = relationship("Loan", back_populates="customer", lazy="dynamic")
    notifications  = relationship("Notification", back_populates="customer", lazy="dynamic")

    def __repr__(self):
        return f"<Customer {self.customer_code} | {self.first_name} {self.last_name}>"
