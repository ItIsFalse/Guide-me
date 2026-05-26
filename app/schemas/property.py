from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .property_unit import PropertyUnitResponse


class PropertyResponse(BaseModel):
    id: int
    region_id: int
    owner_id: Optional[int]
    property_type: str
    name_en: str
    name_uz: Optional[str]
    name_ru: Optional[str]
    description_en: Optional[str]
    description_uz: Optional[str]
    description_ru: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    website: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    working_hours: Optional[str]
    weekend: Optional[str]
    cuisine_type: Optional[str]
    price_level: Optional[str]
    stars: Optional[int]
    has_wifi: bool
    has_parking: bool
    has_breakfast: bool
    has_pool: bool
    has_gym: bool
    has_spa: bool
    has_restaurant: bool
    has_24h_front_desk: bool
    pet_friendly: bool
    chat_enabled: bool
    icon_url: Optional[str]
    cover_url: Optional[str]
    rating_uz: float
    rating_guest: float
    total_reviews: int
    is_active: bool
    moderation_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PropertyDetailResponse(PropertyResponse):
    units: list[PropertyUnitResponse] = []


class PropertyListResponse(BaseModel):
    success: bool = True
    data: list[PropertyResponse] = []
    total: int


class PropertyFilterParams(BaseModel):
    region_id: Optional[int] = None
    property_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    stars: Optional[int] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20