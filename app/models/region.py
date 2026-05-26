from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True)
    name_en = Column(String(100), nullable=False)
    name_uz = Column(String(100), nullable=True)
    name_ru = Column(String(100), nullable=True)
    description = Column(String, nullable=True)  # краткое описание
    icon_url = Column(String(255), nullable=True)  # маленькая иконка
    cover_url = Column(String(255), nullable=True)  # большое фото для фона
    best_season = Column(String(100), nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Связи
    properties = relationship("Property", back_populates="region")
    tours = relationship("Tour", back_populates="region")