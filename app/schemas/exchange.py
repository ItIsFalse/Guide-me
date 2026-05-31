from pydantic import BaseModel
from typing import Optional


class ExchangeRateItem(BaseModel):
    currency: str
    rate: float
    nominal: Optional[int] = 1
    name_uz: Optional[str] = None