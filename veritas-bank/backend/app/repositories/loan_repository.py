# ============================================================
# VERITAS MICROFINANCE BANK - Loan Repository
# OOP: Inheritance (BaseRepository)
# ============================================================
from app.repositories.base_repository import BaseRepository
from app.models.loan import Loan
from sqlalchemy.orm import Session


class LoanRepository(BaseRepository):
    """
    Repository for Loan entity.
    Inherits generic CRUD from BaseRepository.
    OOP Principles: Inheritance, Encapsulation.
    """

    def __init__(self, db: Session):
        super().__init__(Loan, db)

    def get_by_ref(self, loan_ref: str):
        """Fetch a loan by its reference code."""
        return self._db.query(Loan).filter(Loan.loan_ref == loan_ref).first()

    def get_customer_loans(self, customer_id: int):
        """Fetch all loans belonging to a customer."""
        return self._db.query(Loan).filter(
            Loan.customer_id == customer_id
        ).order_by(Loan.created_at.desc()).all()

    def get_pending_loans(self, skip: int = 0, limit: int = 50):
        """Fetch all loans awaiting approval (admin use)."""
        return self._db.query(Loan).filter(
            Loan.status == "PENDING"
        ).order_by(Loan.created_at.asc()).offset(skip).limit(limit).all()

    def get_active_loans(self, skip: int = 0, limit: int = 50):
        """Fetch all currently active / disbursed loans."""
        return self._db.query(Loan).filter(
            Loan.status.in_(["ACTIVE", "DISBURSED"])
        ).order_by(Loan.created_at.desc()).offset(skip).limit(limit).all()
