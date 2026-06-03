from app.services.account_service import BaseService
from app.services.audit_service import AuditService
from sqlalchemy.orm import Session
from datetime import datetime
import secrets
import string


class LoanService(BaseService):
    """Handles loan applications and management."""
 
    INTEREST_RATES = {
        "PERSONAL": 24.0,
        "BUSINESS": 18.0,
        "MICRO": 30.0,
        "AUTO": 20.0,
        "MORTGAGE": 15.0
    }
 
    def __init__(self, db: Session):
        super().__init__(db)
        self._audit = AuditService(db)
 
    def apply(self, customer_id: int, account_id: int, loan_type: str,
              amount: float, tenure_months: int) -> object:
        rate              = self.INTEREST_RATES.get(loan_type, 24.0)
        monthly_rate      = rate / 100 / 12
        monthly_repayment = self._calculate_emi(amount, monthly_rate, tenure_months)
        ref               = f"LN{datetime.utcnow().strftime('%Y%m%d')}" + \
                            "".join(secrets.choice(string.digits) for _ in range(6))
 
        from app.models.all_models import Loan
        loan = Loan(
            account_id        = account_id,
            customer_id       = customer_id,
            loan_ref          = ref,
            loan_type         = loan_type,
            principal_amount  = amount,
            outstanding_amount= amount,
            interest_rate     = rate,
            tenure_months     = tenure_months,
            monthly_repayment = monthly_repayment,
            status            = "PENDING"
        )
        self._db.add(loan)
        self._db.commit()
        self._db.refresh(loan)
 
        self._audit.log(
            event_type="LOAN_APPLICATION", category="ACCOUNT",
            description=f"Loan application NGN {amount:,.2f} [{loan_type}] by customer {customer_id}",
            actor_type="CUSTOMER", actor_id=customer_id,
            target_entity="LOANS", target_id=loan.loan_id
        )
        return loan
 
    def get_customer_loans(self, customer_id: int):
        from app.models.all_models import Loan
        return self._db.query(Loan).filter(Loan.customer_id == customer_id).all()
 
    def _calculate_emi(self, principal: float, monthly_rate: float, months: int) -> float:
        """Calculate Equated Monthly Instalment (EMI)."""
        if monthly_rate == 0:
            return round(principal / months, 2)
        emi = principal * monthly_rate * (1 + monthly_rate) ** months / \
              ((1 + monthly_rate) ** months - 1)
        return round(emi, 2)