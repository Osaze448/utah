# ============================================================
# VERITAS MICROFINANCE BANK - Audit Log Repository
# OOP: Inheritance (BaseRepository), Polymorphism (custom queries)
# ============================================================
from app.repositories.base_repository import BaseRepository
from app.models.audit_log import AuditLog
from sqlalchemy.orm import Session
from datetime import datetime


class AuditLogRepository(BaseRepository):
    """
    Repository for AuditLog entity.
    Inherits generic CRUD from BaseRepository and adds audit-specific queries.
    OOP Principles: Inheritance, Polymorphism (domain-specific methods).
    """

    def __init__(self, db: Session):
        super().__init__(AuditLog, db)

    def log(self, **kwargs) -> AuditLog:
        """Create an audit log entry. Convenience wrapper around create()."""
        return self.create(**kwargs)

    def get_suspicious(self, skip: int = 0, limit: int = 50):
        """Fetch flagged suspicious activity logs."""
        return self._db.query(AuditLog).filter(
            AuditLog.is_suspicious == "Y"
        ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_entity(self, entity: str, entity_id: int, skip: int = 0, limit: int = 50):
        """Fetch audit logs for a specific entity (e.g., ACCOUNTS, LOANS)."""
        return self._db.query(AuditLog).filter(
            AuditLog.target_entity == entity,
            AuditLog.target_id == entity_id
        ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_actor(self, actor_type: str, actor_id: int, skip: int = 0, limit: int = 50):
        """Fetch audit logs by actor (customer or staff)."""
        return self._db.query(AuditLog).filter(
            AuditLog.actor_type == actor_type,
            AuditLog.actor_id == actor_id
        ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_severity(self, severity: str, skip: int = 0, limit: int = 50):
        """Fetch audit logs filtered by severity level."""
        return self._db.query(AuditLog).filter(
            AuditLog.severity == severity
        ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
