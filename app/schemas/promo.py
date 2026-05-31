from pydantic import BaseModel
from typing import Optional


class PromoValidateRequest(BaseModel):
    code: str


class PromoValidateResponse(BaseModel):
    valid: bool
    discount_percent: float = 0
    description: Optional[str] = None