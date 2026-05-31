from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReviewCreateRequest(BaseModel):
    property_id: int
    rating: int  # 1-5
    text_en: Optional[str] = None
    text_uz: Optional[str] = None
    text_ru: Optional[str] = None
    parent_id: Optional[int] = None  # если это ответ на отзыв


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    property_id: int
    parent_id: Optional[int]
    rating: Optional[int]
    text_en: Optional[str]
    text_uz: Optional[str]
    text_ru: Optional[str]
    is_from_resident: bool
    is_active: bool
    user_name: Optional[str] = None      # ← новое
    user_avatar: Optional[str] = None    # ← новое
    created_at: datetime
    replies: list["ReviewResponse"] = []

    model_config = {"from_attributes": True}


class ReviewListResponse(BaseModel):
    success: bool = True
    data: list[ReviewResponse] = []
    total: int
    rating_uz: float = 0.0
    rating_guest: float = 0.0