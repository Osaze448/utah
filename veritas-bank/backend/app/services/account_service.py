# ============================================================
# VERITAS MICROFINANCE BANK - Account Service
# OOP: Inheritance (BaseService), Composition (Repos/Services)
# ============================================================
from datetime import datetime
from decimal import Decimal
import secrets
import string
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.base_service import BaseService
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.repositories.account_repository import AccountRepository
from app.core.config import settings
from app.models.account import Account


class AccountService(BaseService):
    """
    Business logic for managing customer bank accounts.
    OOP Principles:
      - Inheritance: extends BaseService
      - Composition: composes repositories and other services
    """

    def __init__(self, db: Session):
        super().__init__(db)
        self._repo = AccountRepository(db)
        self._audit = AuditService(db)
        self._notif = NotificationService(db)

    def open_account(self, customer_id: int, account_type: str, branch_id: int = 1) -> Account:
        """Open a new banking account for a customer."""
        # Validate account type
        if account_type not in ["SAVINGS", "CURRENT", "FIXED_DEPOSIT"]:
            raise HTTPException(status_code=400, detail="Invalid account type.")

        # Determine interest rate based on type
        interest_rate = Decimal(str(settings.SAVINGS_INTEREST_RATE)) if account_type == "SAVINGS" else \
                        Decimal(str(settings.CURRENT_INTEREST_RATE)) if account_type == "CURRENT" else \
                        Decimal("6.0")  # Default fixed deposit interest

        account_number = self._generate_unique_account_number(account_type)

        # Build account data
        account_data = {
            "customer_id": customer_id,
            "account_number": account_number,
            "account_name": "",  # Populated from customer info in route/caller
            "account_type": account_type,
            "balance": Decimal("0.00"),
            "ledger_balance": Decimal("0.00"),
            "currency": "NGN",
            "status": "ACTIVE",
            "interest_rate": interest_rate,
            "daily_limit": Decimal("500000.00"),
            "overdraft_limit": Decimal("0.00"),
            "tier": 1,
            "branch_id": branch_id
        }

        account = self._repo.create(**account_data)
        self._db.commit()
        self._db.refresh(account)

        # Log audit trail
        self._audit.log(
            event_type="ACCOUNT_OPENED",
            category="ACCOUNT",
            description=f"Opened {account_type} account: {account_number}",
            actor_type="CUSTOMER",
            actor_id=customer_id,
            target_entity="ACCOUNT",
            target_id=account.account_id
        )

        return account

    def get_balance(self, account_number: str) -> dict:
        """Fetch balance details for a specific account."""
        account = self._repo.get_by_number(account_number)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found.")

        return {
            "account_number": account.account_number,
            "account_name": account.account_name,
            "balance": account.balance,
            "ledger_balance": account.ledger_balance,
            "currency": account.currency,
            "status": account.status
        }

    def get_customer_accounts(self, customer_id: int):
        """Retrieve all non-closed accounts for a customer."""
        return self._repo.get_customer_accounts(customer_id)

    def freeze_unfreeze(self, account_number: str, action: str, reason: str, staff_id: int = None) -> Account:
        """Freeze or unfreeze a customer account."""
        account = self._repo.get_by_number(account_number)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found.")

        old_status = account.status
        new_status = "FROZEN" if action == "FREEZE" else "ACTIVE"

        if old_status == new_status:
            raise HTTPException(status_code=400, detail=f"Account is already {old_status}.")

        account.status = new_status
        account.updated_at = datetime.utcnow()
        self._db.commit()

        # Log audit trail
        self._audit.log(
            event_type="ACCOUNT_STATUS_CHANGE",
            category="SECURITY",
            description=f"Account {account_number} status changed from {old_status} to {new_status}. Reason: {reason}",
            actor_type="STAFF" if staff_id else "SYSTEM",
            actor_id=staff_id,
            target_entity="ACCOUNT",
            target_id=account.account_id,
            old_values=f"status: {old_status}",
            new_values=f"status: {new_status}"
        )

        return account

    def _generate_unique_account_number(self, account_type: str) -> str:
        """Generates a unique 10-digit account number."""
        prefix = "10" if account_type == "SAVINGS" else \
                 "20" if account_type == "CURRENT" else "30"

        while True:
            # Generate remaining 8 digits randomly
            suffix = "".join(secrets.choice(string.digits) for _ in range(8))
            account_number = f"{prefix}{suffix}"

            # Check if this account number already exists
            if not self._repo.get_by_number(account_number):
                return account_number