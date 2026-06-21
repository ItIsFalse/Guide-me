from pydantic import BaseModel
from typing import Optional


class PropertyHotelResponse(BaseModel):
    id: int
    property_id: int
    name_en: str
    name_uz: Optional[str] = None
    name_ru: Optional[str] = None
    description_en: Optional[str] = None
    description_uz: Optional[str] = None
    description_ru: Optional[str] = None
    stars: Optional[int] = None
    base_price: float
    discount_price: Optional[float] = None
    max_guests: Optional[int] = None
    bedrooms: Optional[int] = None
    beds: Optional[int] = None
    bathrooms: Optional[int] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    features: Optional[str] = None
    distance_to: Optional[str] = None
    photo_urls: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}