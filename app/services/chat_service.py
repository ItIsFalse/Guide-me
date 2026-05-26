from sqlalchemy.orm import Session
from app.models.chat import ChatMessage
from app.models.property import Property
from app.models.user import User


def get_chat_messages(db: Session, property_id: int, user: User) -> list[ChatMessage]:
    """Сообщения чата: турист видит свои, владелец — все по своему объекту."""
    query = db.query(ChatMessage).filter(ChatMessage.property_id == property_id)

    if user.role == "owner":
        property = db.query(Property).filter(
            Property.id == property_id, Property.owner_id == user.id
        ).first()
        if not property:
            # Не его объект — показываем только его сообщения
            query = query.filter(ChatMessage.sender_id == user.id)
    else:
        query = query.filter(ChatMessage.sender_id == user.id)

    return query.order_by(ChatMessage.created_at.asc()).all()


def send_chat_message(db: Session, user: User, property_id: int, message: str) -> ChatMessage:
    property = db.query(Property).filter(
        Property.id == property_id, Property.is_active == True, Property.chat_enabled == True
    ).first()
    if not property:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Property not found or chat disabled")

    msg = ChatMessage(
        sender_id=user.id,
        property_id=property_id,
        message=message,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg