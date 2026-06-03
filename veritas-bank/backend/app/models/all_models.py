# ============================================================
# VERITAS MICROFINANCE BANK - All Models (Compatibility Shim)
# Existing services import from app.models.all_models
# This re-exports everything from individual model files.
# ============================================================
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.transfer import Transfer
from app.models.loan import Loan
from app.models.audit_log import AuditLog
from app.models.bank_staff import BankStaff
from app.models.notification import Notification

__all__ = [
    "Customer",
    "Account",
    "Transaction",
    "Transfer",
    "Loan",
    "AuditLog",
    "BankStaff",
    "Notification",
]
