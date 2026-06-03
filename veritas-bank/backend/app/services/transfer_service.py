from app.services.account_service import BaseService
from app.services.transaction_service import TransactionService
from app.services.audit_service import AuditService
from sqlalchemy.orm import Session
from datetime import datetime

# Transfer Service (OOP: Inherits TransactionService)
# ─────────────────────────────────────────────
class TransferService(TransactionService):
    """
    Handles intrabank and interbank fund transfers.
    OOP: Inheritance from TransactionService, Method Overriding.
    """
 
    def __init__(self, db: Session):
        super().__init__(db)  # Call parent constructor
 
    def transfer(self, source_acct: str, dest_acct: str, amount: float,
                 narration: str, transfer_type: str, pin: str,
                 customer_id: int, ip_address: str = None) -> dict:
        """Execute a full fund transfer with ACID guarantees."""
        if source_acct == dest_acct:
            raise HTTPException(status_code=400, detail="Cannot transfer to same account.")
        if amount < settings.MIN_TRANSFER_AMOUNT:
            raise HTTPException(status_code=400,
                detail=f"Minimum transfer is NGN {settings.MIN_TRANSFER_AMOUNT:,.2f}")
 
        # Validate source
        src_account = self._get_active_account(source_acct, customer_id)
        customer    = src_account.customer
 
        # Verify PIN
        if not customer.pin_hash:
            raise HTTPException(status_code=400, detail="Transaction PIN not set.")
        if not password_manager.verify_pin(pin, customer.pin_hash):
            raise HTTPException(status_code=401, detail="Incorrect PIN.")
 
        # Calculate fee
        fee        = self._calculate_fee(amount, transfer_type)
        total_debit = amount + fee
 
        if total_debit > float(src_account.balance):
            raise HTTPException(status_code=400,
                detail=f"Insufficient funds. Need NGN {total_debit:,.2f} (incl. fee NGN {fee:,.2f}).")
 
        self._check_daily_limit(src_account, total_debit, "DEBIT")
        self._fraud.analyse(src_account.account_id, amount, "DEBIT", ip_address)
 
        ref = self._generate_ref("XFR")
 
        # Validate destination (intrabank)
        dest_account = None
        dest_name    = "BENEFICIARY"
        if transfer_type == "INTRABANK":
            dest_account = self._acct_repo.get_by_number(dest_acct)
            if not dest_account:
                raise HTTPException(status_code=404, detail="Destination account not found.")
            if dest_account.status != "ACTIVE":
                raise HTTPException(status_code=400, detail="Destination account is not active.")
            dest_name = dest_account.account_name
 
        # DEBIT source
        src_bal_before = float(src_account.balance)
        src_bal_after  = src_bal_before - total_debit
        self._txn_repo.create(
            account_id=src_account.account_id, transaction_ref=f"{ref}-DR",
            transaction_type="DEBIT", amount=total_debit,
            balance_before=src_bal_before, balance_after=src_bal_after,
            description=f"TRF TO {dest_acct}: {narration}",
            channel="MOBILE", status="SUCCESS", ip_address=ip_address
        )
        src_account.balance          = Decimal(str(src_bal_after))
        src_account.ledger_balance   = Decimal(str(src_bal_after))
        src_account.last_transaction = datetime.utcnow()
 
        # CREDIT destination (intrabank only)
        if dest_account:
            dst_bal_before = float(dest_account.balance)
            dst_bal_after  = dst_bal_before + amount
            self._txn_repo.create(
                account_id=dest_account.account_id, transaction_ref=f"{ref}-CR",
                transaction_type="CREDIT", amount=amount,
                balance_before=dst_bal_before, balance_after=dst_bal_after,
                description=f"TRF FROM {source_acct}: {narration}",
                channel="MOBILE", status="SUCCESS", ip_address=ip_address
            )
            dest_account.balance          = Decimal(str(dst_bal_after))
            dest_account.ledger_balance   = Decimal(str(dst_bal_after))
            dest_account.last_transaction = datetime.utcnow()
 
        # Save transfer record
        from app.models.all_models import Transfer
        transfer = Transfer(
            transfer_ref      = ref,
            source_account_id = src_account.account_id,
            dest_account_id   = dest_account.account_id if dest_account else None,
            dest_account_no   = dest_acct,
            dest_bank_name    = "VERITAS MICROFINANCE BANK" if transfer_type == "INTRABANK" else "EXTERNAL BANK",
            dest_account_name = dest_name,
            amount            = amount,
            fee               = fee,
            narration         = narration,
            transfer_type     = transfer_type,
            status            = "SUCCESS",
            completed_at      = datetime.utcnow()
        )
        self._db.add(transfer)
        self._db.commit()
 
        self._notif.send_transaction_alert(customer_id, source_acct, "DEBIT", total_debit, src_bal_after)
        self._audit.log(
            event_type="TRANSFER_SUCCESS", category="TRANSACTION",
            description=f"Transfer NGN {amount:,.2f} from {source_acct} to {dest_acct}. Ref: {ref}",
            actor_type="CUSTOMER", actor_id=customer_id,
            target_entity="TRANSFERS", ip_address=ip_address
        )
        return {
            "transfer_ref": ref, "amount": amount, "fee": fee,
            "dest_account_name": dest_name, "dest_account_no": dest_acct,
            "new_balance": src_bal_after,
            "message": f"Transfer of NGN {amount:,.2f} to {dest_name} successful."
        }
 
    def _calculate_fee(self, amount: float, transfer_type: str) -> float:
        """Override: Calculate transfer fees based on type and amount."""
        if transfer_type == "INTRABANK":
            return 0.0
        if amount <= 5_000:
            base = settings.TRANSFER_FEE_INTERBANK_SMALL
        elif amount <= 50_000:
            base = settings.TRANSFER_FEE_INTERBANK_MEDIUM
        else:
            base = settings.TRANSFER_FEE_INTERBANK_LARGE
        return round(base * 1.075, 2)  # Add 7.5% VAT