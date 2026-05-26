from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class PropertyTag(Base):
    __tablename__ = "property_tags"

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    tag = Column(String(50), nullable=False)

    property = relationship("Property", back_populates="tags")