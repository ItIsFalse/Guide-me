from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime


class BookingRequest(Base):
    __tablename__ = "booking_requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("property_units.id"), nullable=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=True)

    check_in_date = Column(Date, nullable=True)
    check_out_date = Column(Date, nullable=True)
    rooms = Column(Integer, default=1)
    guests = Column(Integer, default=1)

    # pending, contacted, confirmed, cancelled, rejected
    status = Column(String(20), default="pending")

    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # связи
    user = relationship("User", back_populates="booking_requests")
    unit = relationship("PropertyUnit", back_populates="booking_requests")