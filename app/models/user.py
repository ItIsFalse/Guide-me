from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # null для OAuth
    name = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)

    # Роли: guest, resident, owner, moderator, admin
    role = Column(String(20), default="guest", nullable=False)

    preferred_currency = Column(String(3), default="UZS")
    language = Column(String(10), default="uz")

    # OAuth
    google_id = Column(String(255), unique=True, nullable=True)
    apple_id = Column(String(255), unique=True, nullable=True)

    # Статус
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Безопасность — брутфорс защита
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)

    # Токены
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Связи
    properties = relationship("Property", back_populates="owner")
    reviews = relationship("Review", back_populates="user")
    booking_requests = relationship("BookingRequest", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="sender")

    def is_owner(self) -> bool:
        return self.role == "owner"

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_locked(self) -> bool:
        if self.locked_until and self.locked_until > datetime.datetime.utcnow():
            return True
        return False