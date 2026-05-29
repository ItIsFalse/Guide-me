import httpx
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.config import settings
from app.core.security import (
    create_access_token, create_refresh_token, decode_token,
    hash_password, verify_password, generate_token,
)
from app.models.user import User
from app.schemas.auth import TokenResponse
from datetime import datetime, timedelta
import random

AVATARS = [
    "male_1", "male_2", "male_3", "male_4",
    "female_1", "female_2", "female_3", "female_4",
]


# ==================== Google OAuth ====================

async def verify_google_token(id_token: str) -> dict:
    """Проверяет Google id_token и возвращает payload с email, name, picture, sub."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": id_token},
            )
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid Google token")
            payload = response.json()
            return {
                "email": payload.get("email"),
                "name": payload.get("name"),
                "picture": payload.get("picture"),
                "google_id": payload.get("sub"),
            }
    except httpx.HTTPError:
        raise HTTPException(status_code=500, detail="Failed to verify Google token")


def get_or_create_user(db: Session, email: str, google_id: str = None, apple_id: str = None, name: str = None,
                       avatar_url: str = None) -> User:
    """Находит пользователя по email или google_id/apple_id, либо создаёт нового."""
    user = db.query(User).filter(User.email == email).first()

    if not user and google_id:
        user = db.query(User).filter(User.google_id == google_id).first()
    if not user and apple_id:
        user = db.query(User).filter(User.apple_id == apple_id).first()

    if user:
        if google_id and not user.google_id:
            user.google_id = google_id
        if apple_id and not user.apple_id:
            user.apple_id = apple_id
        if name and not user.name:
            user.name = name
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    user = User(
        email=email,
        google_id=google_id,
        apple_id=apple_id,
        name=name,
        avatar_url=avatar_url,
        role="guest",
        is_verified=True,
        last_login=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ==================== JWT Tokens ====================

def generate_tokens(user: User) -> TokenResponse:
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return generate_tokens(user)


# ==================== Email + Password Auth ====================

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
VERIFICATION_TOKEN_EXPIRE_HOURS = 24
RESET_TOKEN_EXPIRE_HOURS = 1


def register_user(db: Session, email: str, password: str, name: str) -> User:
    """Регистрация нового пользователя по email и паролю."""
    # Проверяем что email не занят
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="User with this email already exists")

    user = User(
        email=email,
        password_hash=hash_password(password),
        name=name,
        role="guest",
        is_verified=False,
        verification_token=generate_token(),
        verification_token_expires=datetime.utcnow() + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS),
    )
    user.avatar_url = f"/static/photos/users/{random.choice(AVATARS)}.jpg"
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_with_password(db: Session, email: str, password: str) -> TokenResponse:
    """Вход по email и паролю с защитой от брутфорса."""
    user = db.query(User).filter(User.email == email).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Проверка блокировки
    if user.is_locked():
        remaining = (user.locked_until - datetime.utcnow()).seconds // 60 + 1
        raise HTTPException(
            status_code=423,
            detail=f"Account is locked. Try again in {remaining} minutes"
        )

    # Проверка пароля
    if not user.password_hash or not verify_password(password, user.password_hash):
        user.login_attempts += 1
        if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Успешный вход — сбрасываем счётчик
    user.login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    db.commit()

    return generate_tokens(user)


def verify_email(db: Session, token: str) -> User:
    """Подтверждение email по токену."""
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    if user.verification_token_expires and user.verification_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token expired")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    db.commit()
    return user


def forgot_password(db: Session, email: str) -> str:
    """Отправляет токен для сброса пароля (в реальности — на email, сейчас возвращаем токен)."""
    user = db.query(User).filter(User.email == email, User.is_active == True).first()

    if not user:
        # Не говорим что пользователь не найден — безопасность
        return "If the email exists, a reset link has been sent"

    user.reset_token = generate_token()
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)
    db.commit()

    # В реальном проекте — отправка email
    # Сейчас возвращаем токен для теста
    return user.reset_token


def reset_password(db: Session, token: str, new_password: str) -> User:
    """Сбрасывает пароль по токену."""
    user = db.query(User).filter(User.reset_token == token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")

    if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset token expired")

    user.password_hash = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    user.login_attempts = 0
    user.locked_until = None
    db.commit()
    return user
