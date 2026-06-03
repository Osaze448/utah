# ============================================================
# VERITAS MICROFINANCE BANK - FastAPI Application Entry Point
# ============================================================
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import time
 
from app.core.config import settings
from app.core.database import db_manager
 
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)
 
# ── Create FastAPI app ───────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Veritas Microfinance Bank API
 
Enterprise-grade banking REST API built with FastAPI + Oracle Database.
 
### Features
- 🔐 JWT Authentication (Customer & Staff)
- 💳 Account Management (Savings, Current, Fixed Deposit)
- 💸 Deposits, Withdrawals, Transfers
- 🔍 Transaction History
- 🏦 Loan Management
- 📊 Admin Dashboard & Analytics
- 🛡️ Fraud Detection
- 📋 Audit Logging
""",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)
 
# ── Middleware ───────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round(time.time() - start, 4))
    response.headers["X-API-Version"]  = settings.APP_VERSION
    return response
 
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"← {response.status_code} {request.url.path}")
    return response
 
# ── Global Exception Handler ─────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "An unexpected error occurred. Please try again."}
    )
 
# ── Startup & Shutdown ───────────────────────
@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting Veritas Microfinance Bank API...")
    db_manager.initialize()
    logger.info("✅ Database connected.")
    
    # Automatically create tables in development
    if settings.APP_ENV == "development":
        logger.info("🔧 Creating database tables...")
        try:
            # Import models to register them with SQLAlchemy Base metadata
            from app.models import Customer, Account, Transaction, Transfer, Loan, AuditLog, BankStaff, Notification
            db_manager.create_all_tables()
            logger.info("✅ Database tables created successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {e}")
            
    logger.info(f"📚 Docs available at: http://localhost:{settings.PORT}/api/docs")
 
@app.on_event("shutdown")
async def shutdown():
    logger.info("🔒 Shutting down Veritas Microfinance Bank API...")
 
# ── Health Check ─────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs"
    }
 
@app.get("/health", tags=["Health"])
async def health_check():
    db_ok = db_manager.health_check()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "version": settings.APP_VERSION
    }
 
# ── Include Routers ──────────────────────────
from app.api.routes import auth, customers, accounts, transactions, transfers, loans, admin
 
app.include_router(auth.router,         prefix="/api/v1/auth",         tags=["Authentication"])
app.include_router(customers.router,    prefix="/api/v1/customers",    tags=["Customers"])
app.include_router(accounts.router,     prefix="/api/v1/accounts",     tags=["Accounts"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(transfers.router,    prefix="/api/v1/transfers",    tags=["Transfers"])
app.include_router(loans.router,        prefix="/api/v1/loans",        tags=["Loans"])
app.include_router(admin.router,        prefix="/api/v1/admin",        tags=["Admin"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.1", port=8000, reload=True)