from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.schemas.common import DataResponse
from app.services.chat_service import get_chat_messages, send_chat_message

router = APIRouter()


@router.get("/{property_id}", response_model=DataResponse[list[ChatMessageResponse]])
def get_messages(
    property_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Получить историю чата с пагинацией."""
    messages = get_chat_messages(db, property_id, user, limit, offset)
    return DataResponse(data=messages)


@router.post("/", response_model=DataResponse[ChatMessageResponse])
def send_message(
    data: ChatMessageRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Отправить сообщение."""
    msg = send_chat_message(db, user, data.property_id, data.message)
    return DataResponse(data=ChatMessageResponse.model_validate(msg), message="Message sent")