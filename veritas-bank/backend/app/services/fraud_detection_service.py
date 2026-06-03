from app.services.account_service import BaseService
from app.services.audit_service import AuditService
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta


class FraudDetectionService(BaseService):
    """
    Analyses transactions for suspicious patterns.
    OOP: Polymorphism — multiple check methods with uniform interface.
    """
 
    LARGE_TXN_THRESHOLD = 500_000
    RAPID_TXN_COUNT     = 5
    RAPID_TXN_WINDOW_H  = 1
    HIGH_VOLUME_DAILY   = 2_000_000
 
    def __init__(self, db: Session):
        super().__init__(db)
        self._audit = AuditService(db)
 
    def analyse(self, account_id: int, amount: float,
                txn_type: str, ip_address: str = None) -> dict:
        """Run all fraud checks and return a risk report."""
        flags = []
 
        if self._is_large_transaction(amount):
            flags.append(f"Large transaction: NGN {amount:,.2f}")
 
        if self._is_rapid_transactions(account_id):
            flags.append("High frequency: >5 transactions in 1 hour")
 
        if self._is_high_daily_volume(account_id):
            flags.append("High daily volume: >NGN 2,000,000")
 
        if self._is_unusual_hour():
            flags.append("Transaction at unusual hour (12AM–4AM)")
 
        is_suspicious = len(flags) > 0
 
        if is_suspicious:
            self._audit.log(
                event_type="FRAUD_FLAG",
                category="SECURITY",
                description=f"Suspicious activity on account {account_id}: " + "; ".join(flags),
                severity="CRITICAL",
                actor_type="SYSTEM",
                target_entity="ACCOUNTS",
                target_id=account_id,
                ip_address=ip_address,
                is_suspicious=True,
                flag_reason="; ".join(flags)
            )
 
        return {"is_suspicious": is_suspicious, "flags": flags, "risk_score": len(flags) * 25}
 
    def _is_large_transaction(self, amount: float) -> bool:
        return amount >= self.LARGE_TXN_THRESHOLD
 
    def _is_rapid_transactions(self, account_id: int) -> bool:
        from app.models.all_models import Transaction
        window_start = datetime.utcnow() - timedelta(hours=self.RAPID_TXN_WINDOW_H)
        count = self._db.query(func.count(Transaction.transaction_id)).filter(
            Transaction.account_id == account_id,
            Transaction.status == "SUCCESS",
            Transaction.transaction_date >= window_start
        ).scalar()
        return (count or 0) >= self.RAPID_TXN_COUNT
 
    def _is_high_daily_volume(self, account_id: int) -> bool:
        from app.models.all_models import Transaction
        today = date.today()
        total = self._db.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == account_id,
            Transaction.status == "SUCCESS",
            func.cast(Transaction.transaction_date, func.current_date().__class__) == today
        ).scalar()
        return float(total or 0) >= self.HIGH_DAILY_VOLUME
 
    def _is_unusual_hour(self) -> bool:
        hour = datetime.utcnow().hour
        return 0 <= hour < 4