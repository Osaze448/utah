from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session

class AccountRepository(BaseRepository):
    """Repository for Account entity (Inheritance from BaseRepository)."""
 
    def __init__(self, db: Session):
        from app.models.all_models import Account
        super().__init__(Account, db)
 
    def get_by_number(self, account_number: str):
        from app.models.all_models import Account
        return self._db.query(Account).filter(
            Account.account_number == account_number
        ).first()
 
    def get_customer_accounts(self, customer_id: int):
        from app.models.all_models import Account
        return self._db.query(Account).filter(
            Account.customer_id == customer_id,
            Account.status != "CLOSED"
        ).all()
 
    def get_active_account(self, account_number: str):
        from app.models.all_models import Account
        return self._db.query(Account).filter(
            Account.account_number == account_number,
            Account.status == "ACTIVE"
        ).first()