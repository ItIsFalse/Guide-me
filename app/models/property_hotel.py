from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from app.core.database import Base
import datetime


class PropertyHotel(Base):
    __tablename__ = "property_hotels"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    name_en = Column(String(200), nullable=False)
    name_uz = Column(String(200), nullable=True)
    name_ru = Column(String(200), nullable=True)
    description_en = Column(Text, nullable=True)
    description_uz = Column(Text, nullable=True)
    description_ru = Column(Text, nullable=True)
    stars = Column(Integer, nullable=True)
    base_price = Column(Float, nullable=False, default=0.0)
    discount_price = Column(Float, nullable=True)
    max_guests = Column(Integer, nullable=True, default=2)
    bedrooms = Column(Integer, nullable=True, default=1)
    beds = Column(Integer, nullable=True, default=1)
    bathrooms = Column(Integer, nullable=True, default=1)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    features = Column(Text, nullable=True)  # JSON: ["lake view", "fireplace"]
    distance_to = Column(String(100), nullable=True)  # "10m to lake"
    photo_urls = Column(Text, nullable=True)  # "url1.jpg,url2.jpg"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)