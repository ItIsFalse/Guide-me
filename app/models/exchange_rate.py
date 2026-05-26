from sqlalchemy import Column, Integer, String, Float, DateTime
from app.core.database import Base
import datetime


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True)
    currency_from = Column(String(3), default="USD")
    currency_to = Column(String(3), default="UZS")
    rate = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)