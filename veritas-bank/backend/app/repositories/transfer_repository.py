# ============================================================
# VERITAS MICROFINANCE BANK - Transfer Repository
# OOP: Inheritance (BaseRepository)
# ============================================================
from app.repositories.base_repository import BaseRepository
from app.models.transfer import Transfer
from sqlalchemy.orm import Session


class TransferRepository(BaseRepository):
    """
    Repository for Transfer entity.
    Inherits generic CRUD from BaseRepository.
    OOP Principles: Inheritance, Encapsulation.
    """

    def __init__(self, db: Session):
        super().__init__(Transfer, db)

    def get_by_ref(self, transfer_ref: str):
        """Fetch a transfer by its reference code."""
        return self._db.query(Transfer).filter(
            Transfer.transfer_ref == transfer_ref
        ).first()

    def get_account_transfers(self, account_id: int, skip: int = 0, limit: int = 50):
        """Fetch transfer history for a given account (as source)."""
        return self._db.query(Transfer).filter(
            Transfer.source_account_id == account_id
        ).order_by(Transfer.created_at.desc()).offset(skip).limit(limit).all()

    def get_customer_transfers(self, customer_id: int, skip: int = 0, limit: int = 50):
        """Fetch all transfers initiated by a customer's accounts."""
        from app.models.account import Account
        account_ids = self._db.query(Account.account_id).filter(
            Account.customer_id == customer_id
        ).subquery()
        return self._db.query(Transfer).filter(
            Transfer.source_account_id.in_(account_ids)
        ).order_by(Transfer.created_at.desc()).offset(skip).limit(limit).all()
