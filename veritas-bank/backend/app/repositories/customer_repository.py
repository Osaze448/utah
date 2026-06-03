from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session  
from datetime import datetime
class CustomerRepository(BaseRepository):
    """
    Repository for Customer entity.
    Inherits from BaseRepository (OOP: Inheritance).
    """
 
    def __init__(self, db: Session):
        from app.models.all_models import Customer
        super().__init__(Customer, db)
 
    def get_by_email(self, email: str):
        from app.models.all_models import Customer
        return self._db.query(Customer).filter(Customer.email == email).first()
 
    def get_by_phone(self, phone: str):
        from app.models.all_models import Customer
        return self._db.query(Customer).filter(Customer.phone == phone).first()
 
    def get_by_code(self, customer_code: str):
        from app.models.all_models import Customer
        return self._db.query(Customer).filter(Customer.customer_code == customer_code).first()
 
    def get_active_customers(self, skip=0, limit=100):
        from app.models.all_models import Customer
        return self._db.query(Customer).filter(
            Customer.is_active == "Y",
            Customer.is_blacklisted == "N"
        ).offset(skip).limit(limit).all()
 
    def increment_failed_attempts(self, customer_id: int):
        from app.models.all_models import Customer
        cust = self.get_by_id(customer_id)
        if cust:
            cust.failed_attempts = (cust.failed_attempts or 0) + 1
            self._db.flush()
 
    def reset_failed_attempts(self, customer_id: int):
        from app.models.all_models import Customer
        cust = self.get_by_id(customer_id)
        if cust:
            cust.failed_attempts = 0
            cust.locked_until = None
            cust.last_login = datetime.utcnow()
            self._db.flush()