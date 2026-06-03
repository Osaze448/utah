# ============================================================
# VERITAS MICROFINANCE BANK - Notification Service
# OOP: Inheritance (BaseService), Encapsulation
# ============================================================
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from app.services.base_service import BaseService
from app.models.notification import Notification

logger = logging.getLogger(__name__)


class NotificationService(BaseService):
    """
    Simulates SMS and Email notifications and logs them to database.
    OOP Principles:
      - Inheritance: extends BaseService
    """

    def __init__(self, db: Session):
        super().__init__(db)

    def send_transaction_alert(self, customer_id: int, account_number: str,
                                txn_type: str, amount: float, balance: float,
                                channel: str = "SMS"):
        message = (
            f"Veritas Bank Alert: {'Credit' if txn_type == 'CREDIT' else 'Debit'} "
            f"of NGN {amount:,.2f} on acct ...{account_number[-4:]}. "
            f"Bal: NGN {balance:,.2f}. Not you? Call 0800-VERITAS."
        )
        self._save_notification(customer_id, "TRANSACTION", channel, "Transaction Alert", message)
        logger.info(f"[NOTIFICATION SIMULATED] {channel} -> Customer {customer_id}: {message}")

    def send_otp(self, customer_id: int, otp: str, channel: str = "SMS"):
        message = f"Your Veritas Bank OTP is {otp}. Valid for 5 minutes. Do not share."
        self._save_notification(customer_id, "OTP", channel, "OTP Verification", message)
        logger.info(f"[NOTIFICATION SIMULATED] {channel} -> Customer {customer_id}: {message}")

    def send_login_alert(self, customer_id: int, ip_address: str, device: str = "Mobile App"):
        message = (
            f"Veritas Bank: New login detected on your account from {device}. "
            f"IP: {ip_address}. If this wasn't you, reset your password immediately."
        )
        self._save_notification(customer_id, "SECURITY", "EMAIL", "New Login Alert", message)
        logger.info(f"[NOTIFICATION SIMULATED] EMAIL -> Customer {customer_id}: {message}")

    def _save_notification(self, customer_id: int, notif_type: str,
                            channel: str, subject: str, message: str):
        notif = Notification(
            customer_id=customer_id,
            notif_type=notif_type,
            channel=channel,
            subject=subject,
            message=message,
            status="SENT",
            sent_at=datetime.utcnow()
        )
        self._db.add(notif)
        self._db.flush()
