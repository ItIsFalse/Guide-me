from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class PropertyUnit(Base):
    __tablename__ = "property_units"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    base_price = Column(Float, nullable=False, default=0.0)
    discount_price = Column(Float, nullable=True)
    max_guests = Column(Integer, nullable=True)
    photo_urls = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Связи
    property = relationship("Property", back_populates="units")
    booking_requests = relationship("BookingRequest", back_populates="unit")