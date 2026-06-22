from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PhotoResponse(BaseModel):
    id: int
    entity_type: str  # region, property, property_unit
    entity_id: int
    photo_url: str
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PhotoCreateRequest(BaseModel):
    entity_type: str
    entity_id: int
    photo_url: str
    sort_order: int = 0