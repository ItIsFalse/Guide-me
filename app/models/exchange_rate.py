from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from app.core.database import Base
import datetime


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True)
    currency_code = Column(String(3), nullable=False)  # USD, EUR, RUB
    nominal = Column(Integer, default=1)                # 1 USD, 100 RUB
    rate = Column(Float, nullable=False)                # курс к суму
    date = Column(Date, nullable=False)                 # дата курса
    name_uz = Column(String(100), nullable=True)        # название на узбекском
    created_at = Column(DateTime, default=datetime.datetime.utcnow)