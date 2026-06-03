# ============================================================
# VERITAS MICROFINANCE BANK - Audit Log Model
# OOP: Inheritance (Base), Encapsulation
# ============================================================
from sqlalchemy import (
    Column, Integer, String, DateTime, Text,
    Sequence
)
from datetime import datetime
from app.core.database import Base


class AuditLog(Base):
    """
    Records all significant system events for compliance & security.
    OOP Principles:
      - Inheritance: extends Base
      - Encapsulation: log data as managed state
    """
    __tablename__ = "AUDIT_LOGS"

    # Primary key
    log_id          = Column(Integer, Sequence("SEQ_AUDIT_LOG_ID"), primary_key=True)

    # Event classification
    event_type      = Column(String(50), nullable=False, index=True)
    event_category  = Column(String(30), nullable=False)  # AUTH / TRANSACTION / ACCOUNT / SECURITY

    # Actor
    actor_type      = Column(String(20), default="SYSTEM")  # CUSTOMER / STAFF / SYSTEM
    actor_id        = Column(Integer, nullable=True)

    # Description
    description     = Column(Text, nullable=False)
    severity        = Column(String(20), default="INFO")  # INFO / WARNING / CRITICAL

    # Target
    target_entity   = Column(String(50), nullable=True)   # e.g., ACCOUNTS, LOANS
    target_id       = Column(Integer, nullable=True)

    # Context
    ip_address      = Column(String(50), nullable=True)
    session_id      = Column(String(100), nullable=True)

    # Change tracking
    old_values      = Column(Text, nullable=True)
    new_values      = Column(Text, nullable=True)

    # Fraud flags
    is_suspicious   = Column(String(1), default="N")
    flag_reason     = Column(Text, nullable=True)

    # Timestamps
    created_at      = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.log_id} | {self.event_type} | {self.severity}>"
