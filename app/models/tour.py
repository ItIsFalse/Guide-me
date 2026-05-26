from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class Tour(Base):
    __tablename__ = "tours"

    id = Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    name_en = Column(String(200), nullable=False)
    name_uz = Column(String(200), nullable=True)
    name_ru = Column(String(200), nullable=True)

    description_en = Column(Text, nullable=True)
    description_uz = Column(Text, nullable=True)
    description_ru = Column(Text, nullable=True)

    # длительность в днях
    duration_days = Column(Integer, default=1)

    # средние траты (кэш, пересчитывается)
    avg_total_cost = Column(Float, default=0.0)
    avg_accommodation_cost = Column(Float, default=0.0)
    avg_food_cost = Column(Float, default=0.0)
    avg_transport_cost = Column(Float, default=0.0)
    avg_entertainment_cost = Column(Float, default=0.0)

    # транспорт: public, private, mixed
    transport_type = Column(String(50), default="public")

    cover_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_template = Column(Boolean, default=False)  # готовый тур-пакет
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # связи
    region = relationship("Region", back_populates="tours")
    stops = relationship("TourStop", back_populates="tour", cascade="all, delete-orphan")
    expenses = relationship("UserTourExpense", back_populates="tour", cascade="all, delete-orphan")


class TourStop(Base):
    __tablename__ = "tour_stops"

    id = Column(Integer, primary_key=True)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    stop_order = Column(Integer, nullable=False)  # порядок в маршруте

    # планируемое время на остановке
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    # заметка для этой точки
    note_en = Column(Text, nullable=True)
    note_uz = Column(Text, nullable=True)
    note_ru = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # связи
    tour = relationship("Tour", back_populates="stops")


class UserTourExpense(Base):
    __tablename__ = "user_tour_expenses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=True)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)

    total_spent = Column(Float, default=0.0)
    accommodation_spent = Column(Float, default=0.0)
    food_spent = Column(Float, default=0.0)
    transport_spent = Column(Float, default=0.0)
    entertainment_spent = Column(Float, default=0.0)
    other_spent = Column(Float, default=0.0)

    currency = Column(String(3), default="UZS")
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # связи
    tour = relationship("Tour", back_populates="expenses")