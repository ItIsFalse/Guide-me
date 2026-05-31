from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TourBookingRequest(BaseModel):
    transport_type: str = "car"
    duration_days: int = 1
    promo_code: Optional[str] = None


class TourBookingResponse(BaseModel):
    id: int
    tour_id: int
    user_id: int
    transport_type: str
    duration_days: int
    total_price: float
    discount_applied: float
    promo_code: Optional[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}