from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from app.core.database import Base
import datetime


class TourBooking(Base):
    __tablename__ = "tour_bookings"

    id = Column(Integer, primary_key=True)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transport_type = Column(String(20), default="car")
    duration_days = Column(Integer, default=1)
    total_price = Column(Float, default=0.0)
    discount_applied = Column(Float, default=0.0)
    promo_code = Column(String(50), nullable=True)
    status = Column(String(20), default="pending")  # pending, confirmed, cancelled
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)