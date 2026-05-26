from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from app.core.database import Base
import datetime


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True)

    # полиморфная связь: region, property, property_unit
    entity_type = Column(String(50), nullable=False)  # "region", "property", "property_unit"
    entity_id = Column(Integer, nullable=False)

    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True)

    photo_url = Column(String(255), nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # связи
    property = relationship("Property", back_populates="photos")