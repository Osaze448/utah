# ============================================================
# VERITAS MICROFINANCE BANK - Staff Repository
# OOP: Inheritance (BaseRepository)
# ============================================================
from app.repositories.base_repository import BaseRepository
from app.models.bank_staff import BankStaff
from sqlalchemy.orm import Session


class StaffRepository(BaseRepository):
    """
    Repository for BankStaff entity.
    Inherits generic CRUD from BaseRepository.
    OOP Principles: Inheritance, Encapsulation.
    """

    def __init__(self, db: Session):
        super().__init__(BankStaff, db)

    def get_by_email(self, email: str):
        """Fetch a staff member by email."""
        return self._db.query(BankStaff).filter(BankStaff.email == email).first()

    def get_by_employee_code(self, code: str):
        """Fetch a staff member by employee code."""
        return self._db.query(BankStaff).filter(
            BankStaff.employee_code == code
        ).first()

    def get_active_staff(self, skip: int = 0, limit: int = 100):
        """Fetch all active staff members."""
        return self._db.query(BankStaff).filter(
            BankStaff.is_active == "Y"
        ).offset(skip).limit(limit).all()

    def get_by_role(self, role: str, skip: int = 0, limit: int = 100):
        """Fetch staff members by role."""
        return self._db.query(BankStaff).filter(
            BankStaff.role == role,
            BankStaff.is_active == "Y"
        ).offset(skip).limit(limit).all()
