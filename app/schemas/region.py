from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RegionResponse(BaseModel):
    id: int
    name_en: str
    name_uz: Optional[str]
    name_ru: Optional[str]
    description: Optional[str]
    icon_url: Optional[str]
    cover_url: Optional[str]
    best_season: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RegionListResponse(BaseModel):
    success: bool = True
    data: list[RegionResponse] = []
    total: int = 0