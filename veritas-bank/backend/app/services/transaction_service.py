from app.services.account_service import BaseService
from app.services.audit_service import AuditService
from app.services.fraud_detection_service import FraudDetectionService    
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime

# Transaction Service (OOP Polymorphism)
# ─────────────────────────────────────────────
class TransactionService(BaseService):
    """
    Handles deposit, withdrawal, and transaction history.
    OOP: Polymorphism — process() dispatches to different operations.
    """
 
    def __init__(self, db: Session):
        super().__init__(db)
        self._acct_repo  = AccountRepository(db)
        self._txn_repo   = TransactionRepository(db)
        self._audit      = AuditService(db)
        self._fraud      = FraudDetectionService(db)
        self._notif      = NotificationService(db)
 
    def deposit(self, account_number: str, amount: float,
                description: str, customer_id: int,
                channel: str = "MOBILE", ip_address: str = None) -> dict:
        """Credit an account with the given amount."""
        if amount < settings.MIN_DEPOSIT_AMOUNT:
            raise HTTPException(status_code=400,
                detail=f"Minimum deposit is NGN {settings.MIN_DEPOSIT_AMOUNT:,.2f}")
 
        account = self._get_active_account(account_number, customer_id)
        self._check_daily_limit(account, amount, "CREDIT")
 
        # Fraud check
        self._fraud.analyse(account.account_id, amount, "CREDIT", ip_address)
 
        balance_before = float(account.balance)
        balance_after  = balance_before + amount
        ref = self._generate_ref("DEP")
 
        # Create transaction record
        txn = self._txn_repo.create(
            account_id       = account.account_id,
            transaction_ref  = ref,
            transaction_type = "CREDIT",
            amount           = amount,
            balance_before   = balance_before,
            balance_after    = balance_after,
            description      = description,
            channel          = channel,
            status           = "SUCCESS",
            ip_address       = ip_address
        )
 
        # Update account balance
        account.balance          = Decimal(str(balance_after))
        account.ledger_balance   = Decimal(str(balance_after))
        account.last_transaction = datetime.utcnow()
        self._db.commit()
 
        # Notifications & audit
        self._notif.send_transaction_alert(
            customer_id, account_number, "CREDIT", amount, balance_after
        )
        self._audit.log(
            event_type="DEPOSIT_SUCCESS", category="TRANSACTION",
            description=f"Deposit NGN {amount:,.2f} to {account_number}",
            actor_type="CUSTOMER", actor_id=customer_id,
            target_entity="ACCOUNTS", target_id=account.account_id,
            ip_address=ip_address
        )
        return {
            "transaction_ref": ref,
            "amount": amount,
            "new_balance": balance_after,
            "message": f"Deposit of NGN {amount:,.2f} successful."
        }
 
    def withdraw(self, account_number: str, amount: float, pin: str,
                 customer_id: int, channel: str = "MOBILE",
                 ip_address: str = None) -> dict:
        """Debit an account — validates PIN and sufficient funds."""
        if amount < settings.MIN_WITHDRAWAL_AMOUNT:
            raise HTTPException(status_code=400,
                detail=f"Minimum withdrawal is NGN {settings.MIN_WITHDRAWAL_AMOUNT:,.2f}")
 
        account  = self._get_active_account(account_number, customer_id)
        customer = account.customer
 
        # PIN verification
        if not customer.pin_hash:
            raise HTTPException(status_code=400, detail="Transaction PIN not set.")
        if not password_manager.verify_pin(pin, customer.pin_hash):
            self._audit.log("WRONG_PIN", "SECURITY", "Wrong PIN used for withdrawal",
                            severity="WARNING", actor_id=customer_id, is_suspicious=True)
            raise HTTPException(status_code=401, detail="Incorrect PIN.")
 
        # Overdraft prevention
        available = float(account.balance) + float(account.overdraft_limit)
        if amount > available:
            raise HTTPException(status_code=400,
                detail=f"Insufficient funds. Available: NGN {float(account.balance):,.2f}")
 
        self._check_daily_limit(account, amount, "DEBIT")
        self._fraud.analyse(account.account_id, amount, "DEBIT", ip_address)
 
        balance_before = float(account.balance)
        balance_after  = balance_before - amount
        ref = self._generate_ref("WDR")
 
        self._txn_repo.create(
            account_id       = account.account_id,
            transaction_ref  = ref,
            transaction_type = "DEBIT",
            amount           = amount,
            balance_before   = balance_before,
            balance_after    = balance_after,
            description      = "Cash Withdrawal",
            channel          = channel,
            status           = "SUCCESS",
            ip_address       = ip_address
        )
        account.balance          = Decimal(str(balance_after))
        account.ledger_balance   = Decimal(str(balance_after))
        account.last_transaction = datetime.utcnow()
        self._db.commit()
 
        self._notif.send_transaction_alert(
            customer_id, account_number, "DEBIT", amount, balance_after
        )
        self._audit.log(
            event_type="WITHDRAWAL_SUCCESS", category="TRANSACTION",
            description=f"Withdrawal NGN {amount:,.2f} from {account_number}",
            actor_type="CUSTOMER", actor_id=customer_id,
            ip_address=ip_address
        )
        return {
            "transaction_ref": ref,
            "amount": amount,
            "new_balance": balance_after,
            "message": f"Withdrawal of NGN {amount:,.2f} successful."
        }
 
    def get_history(self, account_number: str, customer_id: int,
                    skip=0, limit=20) -> dict:
        account = self._acct_repo.get_by_number(account_number)
        if not account or account.customer_id != customer_id:
            raise HTTPException(status_code=403, detail="Access denied.")
        txns  = self._txn_repo.get_account_transactions(account.account_id, skip, limit)
        total = self._db.query(func.count()).filter_by(account_id=account.account_id).scalar()
        return {"transactions": txns, "total": total or 0,
                "page": skip // limit + 1, "page_size": limit}
 
    def _get_active_account(self, account_number: str, customer_id: int):
        account = self._acct_repo.get_by_number(account_number)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found.")
        if account.customer_id != customer_id:
            raise HTTPException(status_code=403, detail="Access denied.")
        if account.status == "FROZEN":
            raise HTTPException(status_code=403, detail="Account is frozen.")
        if account.status != "ACTIVE":
            raise HTTPException(status_code=403, detail=f"Account is {account.status}.")
        return account
 
    def _check_daily_limit(self, account, amount: float, txn_type: str):
        daily_spent = self._txn_repo.get_daily_total(account.account_id, txn_type)
        if (daily_spent + amount) > float(account.daily_limit):
            remaining = float(account.daily_limit) - daily_spent
            raise HTTPException(status_code=400,
                detail=f"Daily limit exceeded. Remaining: NGN {remaining:,.2f}")
 
    def _generate_ref(self, prefix: str) -> str:
        ts  = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")[:17]
        rnd = "".join(secrets.choice(string.digits) for _ in range(6))
        return f"{prefix}{ts}{rnd}"