from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, JSON, Enum as SAEnum
from app.db.database import Base
from datetime import datetime
import enum


class ProductCategory(str, enum.Enum):
    ELECTRONICS = "electronics"
    FASHION = "fashion"
    HOME = "home"
    SPORTS = "sports"
    BOOKS = "books"
    BEAUTY = "beauty"


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True)
    name = Column(String(300), nullable=False)
    category = Column(SAEnum(ProductCategory), nullable=False)
    price = Column(Float, nullable=False)
    original_price = Column(Float)
    description = Column(Text)
    image_url = Column(String(500))
    brand = Column(String(200))
    rating = Column(Float, default=4.0)
    review_count = Column(Integer, default=0)
    stock = Column(Integer, default=100)
    popularity_score = Column(Float, default=0.5)
    conversion_rate = Column(Float, default=0.15)
    tags = Column(JSON)  # list of strings
    upsell_ids = Column(JSON)  # list of product_ids
    crosssell_ids = Column(JSON)  # list of product_ids
    created_at = Column(DateTime, default=datetime.utcnow)
