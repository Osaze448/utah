# ============================================================
# VERITAS MICROFINANCE BANK - Notification Model
# OOP: Inheritance (Base), Encapsulation
# ============================================================
from sqlalchemy import (
    Column, Integer, String, DateTime, Text,
    ForeignKey, Sequence
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Notification(Base):
    """
    Stores simulated SMS/Email notifications sent to customers.
    OOP Principles:
      - Inheritance: extends Base
      - Composition: belongs to a Customer
    """
    __tablename__ = "NOTIFICATIONS"

    # Primary key
    notification_id = Column(Integer, Sequence("SEQ_NOTIFICATION_ID"), primary_key=True)
    customer_id     = Column(Integer, ForeignKey("CUSTOMERS.customer_id"), nullable=False, index=True)

    # Notification details
    notif_type      = Column(String(30), nullable=False)   # TRANSACTION / OTP / SECURITY / GENERAL
    channel         = Column(String(10), nullable=False)    # SMS / EMAIL
    subject         = Column(String(200), nullable=True)
    message         = Column(Text, nullable=False)

    # Status
    status          = Column(String(20), default="SENT")    # SENT / FAILED / PENDING
    sent_at         = Column(DateTime, nullable=True)

    # Timestamps
    created_at      = Column(DateTime, default=datetime.utcnow)

    # ── Relationships ────────────────────────
    customer = relationship("Customer", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.notification_id} | {self.notif_type} | {self.channel}>"
