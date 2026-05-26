from pydantic import BaseModel
from typing import Optional


class AIQueryRequest(BaseModel):
    message: str
    budget: Optional[float] = None
    currency: str = "UZS"
    lat: Optional[float] = None
    lon: Optional[float] = None


class AIPropertySuggestion(BaseModel):
    id: int
    name: str
    property_type: str
    description: str
    price_text: str
    rating: float
    region: str


class AIResponse(BaseModel):
    reply: str
    weather: Optional[dict] = None
    suggestions: list[AIPropertySuggestion] = []