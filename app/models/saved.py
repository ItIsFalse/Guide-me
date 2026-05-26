from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.core.database import Base
import datetime


class SavedItem(Base):
    __tablename__ = "saved_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_type = Column(String(50), nullable=False)  # property, tour
    item_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)