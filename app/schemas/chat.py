from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatMessageRequest(BaseModel):
    property_id: int
    message: str


class ChatMessageResponse(BaseModel):
    id: int
    sender_id: int
    property_id: int
    message: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}