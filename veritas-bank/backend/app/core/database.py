# ============================================================
# VERITAS MICROFINANCE BANK - Oracle Database Manager
# OOP: Encapsulation via DatabaseManager class
# ============================================================
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
from app.core.config import settings
import logging
 
logger = logging.getLogger(__name__)
 
Base = declarative_base()
 
 
class DatabaseManager:
    """
    Encapsulates all Oracle database connection logic.
    Implements connection pooling and session management.
    OOP Principle: Encapsulation
    """
 
    _instance = None  # Singleton pattern
 
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
 
    def __init__(self):
        if self._initialized:
            return
        self._engine = None
        self._SessionLocal = None
        self._initialized = True
 
    def initialize(self, database_url: str = None):
        """Initialize the database engine with connection pooling."""
        url = database_url or settings.DATABASE_URL
        try:
            self._engine = create_engine(
                url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,        # Verify connections before use
                pool_recycle=3600,         # Recycle connections every hour
                echo=settings.DEBUG        # Log SQL in debug mode
            )
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            # Register event listeners
            event.listen(self._engine, "connect", self._on_connect)
            logger.info("✅ Oracle Database connection pool initialized.")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
 
    def _on_connect(self, dbapi_con, connection_record):
        """Configure Oracle session on each new connection."""
        cursor = dbapi_con.cursor()
        # Set Oracle session parameters
        cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'")
        cursor.execute("ALTER SESSION SET NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF3'")
        cursor.close()
 
    @property
    def engine(self):
        if self._engine is None:
            self.initialize()
        return self._engine
 
    def get_session(self) -> Session:
        """Create a new database session."""
        if self._SessionLocal is None:
            self.initialize()
        return self._SessionLocal()
 
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction rolled back: {e}")
            raise
        finally:
            session.close()
 
    def create_all_tables(self):
        """Create all tables (development only — use SQL scripts in production)."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("All tables created.")
 
    def health_check(self) -> bool:
        """Check if database is reachable."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1 FROM DUAL"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
 
 
# Singleton instance
db_manager = DatabaseManager()
 
 
# FastAPI dependency
def get_db() -> Generator:
    """FastAPI dependency that provides a database session per request."""
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()