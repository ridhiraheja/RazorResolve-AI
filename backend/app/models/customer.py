from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, JSON, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.database import Base
from datetime import datetime
import enum


class CustomerTier(str, enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    phone = Column(String(20))
    city = Column(String(100))
    state = Column(String(100))
    tier = Column(SAEnum(CustomerTier), default=CustomerTier.BRONZE)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    avg_order_value = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime)

    orders = relationship("Order", back_populates="customer")
    carts = relationship("Cart", back_populates="customer")
