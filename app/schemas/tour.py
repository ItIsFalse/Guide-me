from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import datetime, date


class TourStopPropertyBrief(BaseModel):
    id: int
    name_en: str
    name_uz: Optional[str] = None
    name_ru: Optional[str] = None
    property_type: str
    cover_url: Optional[str] = None
    rating_guest: Optional[float] = None
    description_en: Optional[str] = None
    price_text: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

    model_config = {"from_attributes": True}


class TourStopResponse(BaseModel):
    id: int
    property_id: int
    stop_order: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration_minutes: Optional[int]
    note_en: Optional[str]
    note_uz: Optional[str]
    note_ru: Optional[str]
    property: Optional[TourStopPropertyBrief] = None

    model_config = {"from_attributes": True}


class TourResponse(BaseModel):
    id: int
    region_id: int
    creator_id: Optional[int]
    name_en: str
    name_uz: Optional[str]
    name_ru: Optional[str]
    description_en: Optional[str]
    description_uz: Optional[str]
    description_ru: Optional[str]
    duration_days: int
    avg_total_cost: float
    avg_accommodation_cost: float
    avg_food_cost: float
    avg_transport_cost: float
    avg_entertainment_cost: float
    transport_type: str
    cover_url: Optional[str]
    is_active: bool
    is_template: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TourDetailResponse(TourResponse):
    stops: list[TourStopResponse] = []


class TourCreateRequest(BaseModel):
    region_id: int
    name_en: str
    name_uz: Optional[str] = None
    name_ru: Optional[str] = None
    description_en: Optional[str] = None
    duration_days: int = 1
    transport_type: str = "public"
    property_ids: list[int] = []  # порядок = порядок в маршруте


class TourExpenseRequest(BaseModel):
    tour_id: Optional[int] = None
    region_id: Optional[int] = None
    total_spent: float = 0.0
    accommodation_spent: float = 0.0
    food_spent: float = 0.0
    transport_spent: float = 0.0
    entertainment_spent: float = 0.0
    other_spent: float = 0.0
    currency: str = "UZS"
    comment: Optional[str] = None

    @model_validator(mode="after")
    def check_tour_or_region(self):
        if not self.tour_id and not self.region_id:
            raise ValueError("tour_id or region_id is required")
        return self


class TourExpenseResponse(BaseModel):
    id: int
    user_id: int
    tour_id: Optional[int]
    region_id: Optional[int]
    total_spent: float
    accommodation_spent: float
    food_spent: float
    transport_spent: float
    entertainment_spent: float
    other_spent: float
    currency: str
    comment: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class TourAverageResponse(BaseModel):
    region_id: int
    region_name: str
    total_reports: int
    avg_total: float
    avg_accommodation: float
    avg_food: float
    avg_transport: float
    avg_entertainment: float


class NavigationStepResponse(BaseModel):
    stop_order: int
    property_id: int
    property_name: str
    property_type: str
    lat: float
    lon: float
    duration_minutes: int  # время на точке
    travel_time_minutes: int  # время в пути от предыдущей
    distance_km: float  # расстояние от предыдущей


class RouteRequest(BaseModel):
    property_id: int
    user_lat: float
    user_lon: float
    transport_type: str = "car"


class RouteResponse(BaseModel):
    from_lat: float
    from_lon: float
    to_name: str
    to_lat: float
    to_lon: float
    distance_km: float
    time_minutes: int
    transport: str
