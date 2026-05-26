from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)

    # enum: hotel, museum, park, restaurant, shop, entertainment, other
    property_type = Column(String(50), nullable=False, default="other")

    # мультиязычные названия
    name_en = Column(String(200), nullable=False)
    name_uz = Column(String(200), nullable=True)
    name_ru = Column(String(200), nullable=True)

    # мультиязычные описания
    description_en = Column(Text, nullable=True)
    description_uz = Column(Text, nullable=True)
    description_ru = Column(Text, nullable=True)

    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)

    # общие поля для всех типов
    website = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)

    # режим работы
    working_hours = Column(String(100), nullable=True)  # "09:00-18:00"
    weekend = Column(String(100), nullable=True)        # "Sunday"

    # специфичные для ресторанов
    cuisine_type = Column(String(100), nullable=True)
    price_level = Column(String(10), nullable=True)     # low, medium, high

    # специфичные для отелей/жилья
    stars = Column(Integer, nullable=True)
    check_in_time = Column(String(20), nullable=True)   # "14:00"
    check_out_time = Column(String(20), nullable=True)  # "12:00"

    # amenities (булевы флаги для отелей)
    has_wifi = Column(Boolean, default=False)
    has_parking = Column(Boolean, default=False)
    has_breakfast = Column(Boolean, default=False)
    has_pool = Column(Boolean, default=False)
    has_gym = Column(Boolean, default=False)
    has_spa = Column(Boolean, default=False)
    has_restaurant = Column(Boolean, default=False)
    has_24h_front_desk = Column(Boolean, default=False)
    pet_friendly = Column(Boolean, default=False)

    # доставка (для ресторанов и магазинов)
    has_delivery = Column(Boolean, default=False)
    has_takeaway = Column(Boolean, default=False)

    # чат с владельцем
    chat_enabled = Column(Boolean, default=False)

    # фото
    icon_url = Column(String(255), nullable=True)
    cover_url = Column(String(255), nullable=True)

    # рейтинги (кэш, пересчитываются из reviews)
    rating_uz = Column(Float, default=0.0)     # средняя от резидентов
    rating_guest = Column(Float, default=0.0)  # средняя от нерезидентов
    total_reviews = Column(Integer, default=0)

    # модерация
    is_active = Column(Boolean, default=False)
    moderation_status = Column(String(20), default="pending")  # pending, approved, rejected
    moderation_comment = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # связи
    owner = relationship("User", back_populates="properties")
    region = relationship("Region", back_populates="properties")
    units = relationship("PropertyUnit", back_populates="property", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="property", cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="property", cascade="all, delete-orphan")
    tags = relationship("PropertyTag", back_populates="property", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="property", cascade="all, delete-orphan")