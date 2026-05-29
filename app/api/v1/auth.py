from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import (
    GoogleAuthRequest, AppleAuthRequest, RefreshRequest, TokenResponse,
    RegisterRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import DataResponse
from app.services.auth_service import (
    verify_google_token, get_or_create_user, generate_tokens, refresh_access_token,
    register_user, login_with_password, verify_email, forgot_password, reset_password,
)
from app.core.security import get_current_user
from app.models.user import User
from fastapi import HTTPException

router = APIRouter()

# ==================== OAuth ====================

@router.post("/google", response_model=DataResponse[TokenResponse])
async def google_login(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Вход через Google OAuth."""
    google_data = await verify_google_token(request.id_token)
    user = get_or_create_user(
        db,
        email=google_data["email"],
        google_id=google_data["google_id"],
        name=google_data.get("name"),
        avatar_url=google_data.get("picture"),
    )
    tokens = generate_tokens(user)
    return DataResponse(data=tokens, message="Login successful")


@router.post("/apple", response_model=DataResponse[TokenResponse])
async def apple_login(request: AppleAuthRequest, db: Session = Depends(get_db)):
    """Вход через Apple OAuth (заглушка)."""
    from fastapi import HTTPException
    raise HTTPException(status_code=501, detail="Apple auth coming soon")


# ==================== Email + Password ====================

@router.post("/register", response_model=DataResponse[TokenResponse])
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Регистрация по email и паролю."""
    user = register_user(db, request.email, request.password, request.name)
    tokens = generate_tokens(user)
    return DataResponse(
        data=tokens,
        message="Registration successful. Please verify your email."
    )


@router.post("/login", response_model=DataResponse[TokenResponse])
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Вход по email и паролю."""
    tokens = login_with_password(db, request.email, request.password)
    return DataResponse(data=tokens, message="Login successful")


@router.post("/verify-email", response_model=DataResponse)
def verify_email_endpoint(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Подтверждение email по токену."""
    verify_email(db, request.token)
    return DataResponse(message="Email verified successfully")


@router.post("/forgot-password", response_model=DataResponse)
def forgot_password_endpoint(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Запрос на сброс пароля. Токен отправляется на email (пока возвращается в ответе)."""
    reset_token = forgot_password(db, request.email)
    return DataResponse(
        message="If the email exists, a reset link has been sent",
        data={"reset_token": reset_token} if reset_token != "If the email exists, a reset link has been sent" else None
    )


@router.post("/reset-password", response_model=DataResponse)
def reset_password_endpoint(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Сброс пароля по токену."""
    reset_password(db, request.token, request.new_password)
    return DataResponse(message="Password reset successful")


# ==================== Tokens & Profile ====================

@router.post("/refresh", response_model=DataResponse[TokenResponse])
def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    """Обновить access_token."""
    tokens = refresh_access_token(db, request.refresh_token)
    return DataResponse(data=tokens, message="Token refreshed")

@router.put("/me", response_model=DataResponse[UserResponse])
def update_profile(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Обновить профиль текущего пользователя."""
    if data.name is not None:
        user.name = data.name
    if data.preferred_currency is not None:
        if data.preferred_currency not in ("UZS", "USD"):
            raise HTTPException(status_code=400, detail="Currency must be UZS or USD")
        user.preferred_currency = data.preferred_currency
    if data.language is not None:
        if data.language not in ("uz", "ru", "en"):
            raise HTTPException(status_code=400, detail="Language must be uz, ru, or en")
        user.language = data.language
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url
    db.commit()
    db.refresh(user)
    return DataResponse(data=UserResponse.model_validate(user), message="Profile updated")

@router.get("/me", response_model=DataResponse[UserResponse])
def get_me(user: User = Depends(get_current_user)):
    """Возвращает профиль текущего пользователя."""
    return DataResponse(data=user)