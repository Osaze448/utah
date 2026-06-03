from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session

class TransactionRepository(BaseRepository):
    """Repository for Transaction entity."""
 
    def __init__(self, db: Session):
        from app.models.all_models import Transaction
        super().__init__(Transaction, db)
 
    def get_account_transactions(self, account_id: int, skip=0, limit=50):
        from app.models.all_models import Transaction
        return self._db.query(Transaction).filter(
            Transaction.account_id == account_id
        ).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()
 
    def get_by_ref(self, ref: str):
        from app.models.all_models import Transaction
        return self._db.query(Transaction).filter(
            Transaction.transaction_ref == ref
        ).first()
 
    def get_daily_total(self, account_id: int, txn_type: str) -> float:
        from app.models.all_models import Transaction
        from sqlalchemy import func, cast, Date
        today = datetime.utcnow().date()
        result = self._db.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == account_id,
            Transaction.transaction_type == txn_type,
            Transaction.status == "SUCCESS",
            func.cast(Transaction.transaction_date, Date) == today
        ).scalar()
        return float(result or 0)