# ============================================================
# VERITAS MICROFINANCE BANK - Schemas Package Entry Point
# ============================================================
from app.schemas.auth import (
    CustomerLoginRequest,
    StaffLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    ChangePasswordRequest,
    SetPinRequest
)
from app.schemas.customer import (
    CustomerRegisterRequest,
    CustomerResponse,
    CustomerProfileResponse,
    UpdateProfileRequest
)
from app.schemas.account import (
    CreateAccountRequest,
    AccountResponse,
    AccountBalanceResponse,
    FreezeAccountRequest
)
from app.schemas.transaction import (
    DepositRequest,
    WithdrawRequest,
    TransferRequest,
    TransactionResponse,
    TransactionHistoryResponse,
    TransferResponse
)
from app.schemas.loan import (
    LoanApplicationRequest,
    LoanResponse,
    LoanListResponse
)
from app.schemas.admin import (
    DashboardStatsResponse,
    StaffCreateRequest,
    StaffResponse
)
