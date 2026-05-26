from pydantic import BaseModel
from typing import Optional


class PropertyUnitResponse(BaseModel):
    id: int
    property_id: int
    unit_type: str
    name_en: str
    name_uz: Optional[str]
    name_ru: Optional[str]
    description_en: Optional[str]
    description_uz: Optional[str]
    description_ru: Optional[str]
    base_price: float
    discount_price: Optional[float]
    max_guests: Optional[int]
    bedrooms: Optional[int]
    photo_urls: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}