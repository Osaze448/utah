# ============================================================
# VERITAS MICROFINANCE BANK - Base Service
# OOP: Abstraction, Encapsulation
# ============================================================
from sqlalchemy.orm import Session


class BaseService:
    """
    Abstract base service holding the database session.
    OOP Principles:
      - Abstraction: hides base session injection
      - Encapsulation: encapsulates SQLAlchemy session inside private state
    """
    def __init__(self, db: Session):
        self._db = db
