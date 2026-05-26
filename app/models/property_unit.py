from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class PropertyUnit(Base):
    __tablename__ = "property_units"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)

    # тип юнита: room, cottage, suite, ticket_standard, ticket_vip, entrance
    unit_type = Column(String(50), nullable=False, default="room")

    name_en = Column(String(200), nullable=False)
    name_uz = Column(String(200), nullable=True)
    name_ru = Column(String(200), nullable=True)

    description_en = Column(Text, nullable=True)
    description_uz = Column(Text, nullable=True)
    description_ru = Column(Text, nullable=True)

    # цены всегда в сумах
    base_price = Column(Float, nullable=False, default=0.0)
    discount_price = Column(Float, nullable=True)

    max_guests = Column(Integer, nullable=True, default=1)
    bedrooms = Column(Integer, nullable=True, default=1)
    beds = Column(Integer, nullable=True, default=1)
    bathrooms = Column(Integer, nullable=True, default=1)

    # фото юнита (можно хранить JSON-массив URL)
    photo_urls = Column(Text, nullable=True)  # "url1,url2,url3"

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # связи
    property = relationship("Property", back_populates="units")
    booking_requests = relationship("BookingRequest", back_populates="unit")