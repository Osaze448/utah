from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy.orm import Session
from app.core.database import Base
from datetime import datetime

ModelType = TypeVar("ModelType", bound=Base)
 
 
class BaseRepository(Generic[ModelType]):
    """
    Abstract base repository implementing generic CRUD operations.
    All entity repositories inherit from this class.
    OOP Principles: Abstraction, Inheritance, Encapsulation
    """
 
    def __init__(self, model: Type[ModelType], db: Session):
        self._model = model   # Encapsulated model type
        self._db = db         # Encapsulated database session
 
    # ── Create ──────────────────────────────
    def create(self, **kwargs) -> ModelType:
        """Insert a new record and return it."""
        instance = self._model(**kwargs)
        self._db.add(instance)
        self._db.flush()
        self._db.refresh(instance)
        return instance
 
    # ── Read ────────────────────────────────
    def get_by_id(self, record_id: int) -> Optional[ModelType]:
        """Fetch a single record by primary key."""
        return self._db.query(self._model).filter(
            self._get_pk_column() == record_id
        ).first()
 
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Fetch all records with pagination."""
        return self._db.query(self._model).offset(skip).limit(limit).all()
 
    def count(self) -> int:
        """Return total number of records."""
        return self._db.query(self._model).count()
 
    # ── Update ──────────────────────────────
    def update(self, record_id: int, **kwargs) -> Optional[ModelType]:
        """Update fields on an existing record."""
        instance = self.get_by_id(record_id)
        if instance is None:
            return None
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        if hasattr(instance, "updated_at"):
            instance.updated_at = datetime.utcnow()
        self._db.flush()
        self._db.refresh(instance)
        return instance
 
    # ── Delete ──────────────────────────────
    def delete(self, record_id: int) -> bool:
        """Soft-delete or hard-delete a record."""
        instance = self.get_by_id(record_id)
        if instance is None:
            return False
        # Prefer soft delete
        if hasattr(instance, "is_active"):
            instance.is_active = "N"
            instance.updated_at = datetime.utcnow()
        else:
            self._db.delete(instance)
        self._db.flush()
        return True
 
    def _get_pk_column(self):
        """Return the primary key column for this model."""
        from sqlalchemy import inspect
        mapper = inspect(self._model)
        pk = mapper.primary_key[0]
        return getattr(self._model, pk.name)
 
    def exists(self, **filters) -> bool:
        """Check if any record matches the given filters."""
        query = self._db.query(self._model)
        for attr, value in filters.items():
            query = query.filter(getattr(self._model, attr) == value)
        return query.first() is not None