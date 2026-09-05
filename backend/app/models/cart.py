from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, JSON, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
import enum


class CartStatus(str, enum.Enum):
    ACTIVE = "active"
    ABANDONED = "abandoned"
    CONVERTED = "converted"
    RECOVERED = "recovered"


class Cart(Base):
    __tablename__ = "carts"

    id = Column(String(36), primary_key=True)
    customer_id = Column(String(36), ForeignKey("customers.id"))
    status = Column(SAEnum(CartStatus), default=CartStatus.ACTIVE)
    items = Column(JSON)  # list of {product_id, name, qty, price}
    total_value = Column(Float, default=0.0)
    item_count = Column(Integer, default=0)
    intent_score = Column(Float, default=0.0)
    conversion_probability = Column(Float, default=0.0)
    recommended_intervention = Column(Text)
    expected_recovery = Column(Float, default=0.0)
    abandoned_at = Column(DateTime)
    recovered_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="carts")
