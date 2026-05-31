from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    body: Optional[str]
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}