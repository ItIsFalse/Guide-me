from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)

    # вложенность: ответ владельца на отзыв
    parent_id = Column(Integer, ForeignKey("reviews.id"), nullable=True)

    rating = Column(Integer, nullable=True)  # 1-5, null если это ответ без оценки

    text_en = Column(Text, nullable=True)
    text_uz = Column(Text, nullable=True)
    text_ru = Column(Text, nullable=True)

    # от резидента или гостя
    is_from_resident = Column(Boolean, default=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # связи
    user = relationship("User", back_populates="reviews")
    property = relationship("Property", back_populates="reviews")
    parent = relationship("Review", remote_side=[id], backref="replies")