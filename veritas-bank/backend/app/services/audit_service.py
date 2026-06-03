# ============================================================
# VERITAS MICROFINANCE BANK - Audit Service
# OOP: Inheritance (BaseService), Composition (AuditLogRepository)
# ============================================================
from sqlalchemy.orm import Session
from app.services.base_service import BaseService
from app.repositories.audit_log_repository import AuditLogRepository
from app.models.audit_log import AuditLog


class AuditService(BaseService):
    """
    Logs all significant system events to AUDIT_LOGS table.
    OOP Principles:
      - Inheritance: extends BaseService
      - Composition: composes AuditLogRepository for database interactions
    """

    def __init__(self, db: Session):
        super().__init__(db)
        self._repo = AuditLogRepository(db)

    def log(self, event_type: str, category: str, description: str,
            actor_type: str = "SYSTEM", actor_id: int = None,
            severity: str = "INFO", target_entity: str = None,
            target_id: int = None, ip_address: str = None,
            session_id: str = None, old_values: str = None,
            new_values: str = None, is_suspicious: bool = False,
            flag_reason: str = None):
        self._repo.log(
            event_type=event_type,
            event_category=category,
            actor_type=actor_type,
            actor_id=actor_id,
            description=description,
            severity=severity,
            target_entity=target_entity,
            target_id=target_id,
            ip_address=ip_address,
            session_id=session_id,
            old_values=old_values,
            new_values=new_values,
            is_suspicious="Y" if is_suspicious else "N",
            flag_reason=flag_reason
        )

    def get_all(self, skip=0, limit=50):
        return self._db.query(AuditLog).order_by(
            AuditLog.created_at.desc()
        ).offset(skip).limit(limit).all()

    def get_suspicious(self, skip=0, limit=50):
        return self._repo.get_suspicious(skip, limit)