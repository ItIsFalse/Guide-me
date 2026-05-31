from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import date, datetime


class BookingPropertyBrief(BaseModel):
    id: int
    name_en: str
    cover_url: Optional[str]
    address: Optional[str]
    model_config = {"from_attributes": True}


class BookingRequestCreate(BaseModel):
    unit_id: Optional[int] = None
    property_id: Optional[int] = None
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    rooms: int = 1
    guests: int = 1
    message: Optional[str] = None

    @model_validator(mode="after")
    def check_at_least_one_target(self):
        if not self.unit_id and not self.property_id:
            raise ValueError("unit_id or property_id is required")
        return self


class BookingRequestResponse(BaseModel):
    id: int
    user_id: int
    unit_id: Optional[int]
    property_id: Optional[int]
    property: Optional[BookingPropertyBrief] = None
    check_in_date: Optional[date]
    check_out_date: Optional[date]
    rooms: int
    guests: int
    status: str
    message: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}