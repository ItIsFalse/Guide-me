from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SavedPropertyBrief(BaseModel):
    id: int
    name_en: str
    name_uz: Optional[str] = None
    name_ru: Optional[str] = None
    property_type: str
    cover_url: Optional[str] = None
    address: Optional[str] = None
    rating_guest: Optional[float] = None
    price_text: Optional[str] = None

    model_config = {"from_attributes": True}


class SavedTourBrief(BaseModel):
    id: int
    name_en: str
    name_uz: Optional[str] = None
    name_ru: Optional[str] = None
    cover_url: Optional[str] = None
    duration_days: Optional[int] = None
    transport_type: Optional[str] = None

    model_config = {"from_attributes": True}


class SavedItemResponse(BaseModel):
    id: int
    item_type: str
    item_id: int
    created_at: datetime
    property: Optional[SavedPropertyBrief] = None
    tour: Optional[SavedTourBrief] = None

    model_config = {"from_attributes": True}