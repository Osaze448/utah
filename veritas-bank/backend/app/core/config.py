# ============================================================
# VERITAS MICROFINANCE BANK - Application Configuration
# ============================================================
import os
import urllib.parse
from pydantic_settings import BaseSettings
from functools import lru_cache
 
 
class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Veritas Microfinance Bank API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
 
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
 
    # Oracle Database
    ORACLE_USER: str = os.getenv("ORACLE_USER", "veritas_admin")
    ORACLE_PASSWORD: str = os.getenv("ORACLE_PASSWORD", "VeritasDB@2024")
    ORACLE_HOST: str = os.getenv("ORACLE_HOST", "localhost")
    ORACLE_PORT: int = int(os.getenv("ORACLE_PORT", "1521"))
    ORACLE_SERVICE: str = os.getenv("ORACLE_SERVICE", "VERITASDB")
 
    @property
    def DATABASE_URL(self) -> str:
        escaped_password = urllib.parse.quote_plus(self.ORACLE_PASSWORD)
        return (
            f"oracle+oracledb://{self.ORACLE_USER}:{escaped_password}"
            f"@{self.ORACLE_HOST}:{self.ORACLE_PORT}/?service_name={self.ORACLE_SERVICE}"
        )
 
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "veritas-super-secret-jwt-key-2024-enterprise")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
 
    # Security
    BCRYPT_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_MINUTES: int = 30
 
    # Banking Rules
    MIN_DEPOSIT_AMOUNT: float = 100.0
    MIN_WITHDRAWAL_AMOUNT: float = 100.0
    MIN_TRANSFER_AMOUNT: float = 100.0
    MAX_DAILY_TRANSFER: float = 5_000_000.0
    SAVINGS_INTEREST_RATE: float = 4.5
    CURRENT_INTEREST_RATE: float = 1.5
    TRANSFER_FEE_INTRABANK: float = 0.0
    TRANSFER_FEE_INTERBANK_SMALL: float = 10.75   # <= 5000
    TRANSFER_FEE_INTERBANK_MEDIUM: float = 26.88  # <= 50000
    TRANSFER_FEE_INTERBANK_LARGE: float = 53.75   # > 50000
 
    # Notification (simulated)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_EMAIL: str = os.getenv("SMTP_EMAIL", "noreply@veritasbank.com")
    SMS_API_KEY: str = os.getenv("SMS_API_KEY", "sim-key-xxxx")
 
    # CORS
    ALLOWED_ORIGINS: list = ["*"]
 
    class Config:
        env_file = ".env"
        case_sensitive = True
 
 
@lru_cache()
def get_settings() -> Settings:
    return Settings()
 
 
settings = get_settings()