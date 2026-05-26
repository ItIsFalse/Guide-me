from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    google_id: Optional[str] = None
    apple_id: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = "guest"


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    avatar_url: Optional[str]
    role: str
    preferred_currency: str
    language: str
    is_verified: bool
    is_active: bool
    login_attempts: int
    locked_until: Optional[datetime]
    last_login: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: Optional[str] = None
    preferred_currency: Optional[str] = None
    language: Optional[str] = None
    avatar_url: Optional[str] = None