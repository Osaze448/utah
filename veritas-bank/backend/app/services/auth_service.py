# ============================================================
# VERITAS MICROFINANCE BANK - Auth Service
# OOP: Inheritance (BaseService), Composition (Repos/Services)
# ============================================================
from datetime import datetime
import secrets
import string
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.base_service import BaseService
from app.services.audit_service import AuditService
from app.services.notification_service import NotificationService
from app.repositories.customer_repository import CustomerRepository
from app.core.config import settings
from app.core.security import password_manager, token_manager


class AuthService(BaseService):
    """
    Handles customer and staff authentication.
    OOP Principles:
      - Inheritance: extends BaseService
      - Composition: composes customer repository, audit, and notification services
    """

    def __init__(self, db: Session):
        super().__init__(db)
        self._cust_repo  = CustomerRepository(db)
        self._audit      = AuditService(db)
        self._notif      = NotificationService(db)

    def register_customer(self, data: dict) -> dict:
        """Register a new customer account."""
        # Check uniqueness
        if self._cust_repo.exists(email=data["email"]):
            raise HTTPException(status_code=400, detail="Email already registered.")
        if self._cust_repo.exists(phone=data["phone"]):
            raise HTTPException(status_code=400, detail="Phone number already registered.")

        # Hash password
        password = data.pop("password")
        data["password_hash"] = password_manager.hash_password(password)
        data["customer_code"] = self._generate_customer_code()

        customer = self._cust_repo.create(**data)
        self._db.commit()
        self._db.refresh(customer)

        self._audit.log(
            event_type="CUSTOMER_REGISTERED",
            category="ACCOUNT",
            description=f"New customer registered: {customer.email}",
            actor_type="CUSTOMER",
            actor_id=customer.customer_id
        )
        return customer

    def login_customer(self, email: str, password: str, ip_address: str = None) -> dict:
        """Authenticate a customer and return JWT tokens."""
        customer = self._cust_repo.get_by_email(email)

        if not customer:
            self._audit.log("LOGIN_FAILED", "AUTH", f"Login attempt with unknown email: {email}",
                            severity="WARNING", ip_address=ip_address, is_suspicious=True)
            raise HTTPException(status_code=401, detail="Invalid credentials.")

        # Check lockout
        if customer.locked_until and customer.locked_until > datetime.utcnow():
            remaining = int((customer.locked_until - datetime.utcnow()).seconds / 60)
            raise HTTPException(status_code=403,
                detail=f"Account locked. Try again in {remaining} minutes.")

        if not password_manager.verify_password(password, customer.password_hash):
            self._cust_repo.increment_failed_attempts(customer.customer_id)
            self._db.commit()
            self._audit.log("LOGIN_FAILED", "AUTH", f"Wrong password for: {email}",
                            severity="WARNING", actor_id=customer.customer_id,
                            ip_address=ip_address)
            raise HTTPException(status_code=401, detail="Invalid credentials.")

        # Successful login
        self._cust_repo.reset_failed_attempts(customer.customer_id)
        self._db.commit()

        access_token  = token_manager.create_access_token(
            {"sub": str(customer.customer_id), "user_type": "customer", "email": customer.email}
        )
        refresh_token = token_manager.create_refresh_token(
            {"sub": str(customer.customer_id), "user_type": "customer"}
        )

        self._audit.log("LOGIN_SUCCESS", "AUTH", f"Customer logged in: {email}",
                        actor_type="CUSTOMER", actor_id=customer.customer_id,
                        ip_address=ip_address)
        self._notif.send_login_alert(customer.customer_id, ip_address or "Unknown")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_type": "customer"
        }

    def login_staff(self, email: str, password: str, ip_address: str = None) -> dict:
        """Authenticate bank staff."""
        from app.models.bank_staff import BankStaff
        staff = self._db.query(BankStaff).filter(BankStaff.email == email).first()

        if not staff or not password_manager.verify_password(password, staff.password_hash):
            self._audit.log("STAFF_LOGIN_FAILED", "AUTH",
                            f"Failed staff login: {email}", severity="WARNING",
                            ip_address=ip_address, is_suspicious=True)
            raise HTTPException(status_code=401, detail="Invalid staff credentials.")

        if staff.is_active == "N":
            raise HTTPException(status_code=403, detail="Staff account is inactive.")

        staff.last_login = datetime.utcnow()
        self._db.commit()

        access_token = token_manager.create_access_token(
            {"sub": str(staff.staff_id), "user_type": "staff",
             "role": staff.role, "email": staff.email}
        )
        refresh_token = token_manager.create_refresh_token(
            {"sub": str(staff.staff_id), "user_type": "staff", "role": staff.role}
        )
        self._audit.log("STAFF_LOGIN_SUCCESS", "AUTH",
                        f"Staff logged in: {email} [{staff.role}]",
                        actor_type="STAFF", actor_id=staff.staff_id,
                        ip_address=ip_address)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_type": "staff",
            "role": staff.role
        }

    def _generate_customer_code(self) -> str:
        month  = datetime.utcnow().strftime("%y%m")
        suffix = "".join(secrets.choice(string.digits) for _ in range(5))
        return f"VTB{month}{suffix}"