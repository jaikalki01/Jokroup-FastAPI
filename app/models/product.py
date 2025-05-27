from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, default=0.0)
    images = Column(JSON)  # Store list of image URLs as JSON
    category_id = Column(Integer, nullable=False)  # Usually an integer FK id
    subcategory_id = Column(Integer, nullable=False)
    colors = Column(JSON)  # List of strings
    sizes = Column(JSON)   # List of strings
    in_stock = Column(Boolean, default=True)
    rating = Column(Float, default=0.0)
    reviews = Column(Integer, default=0)
    featured = Column(Boolean, default=False)
    best_seller = Column(Boolean, default=False)
    new_arrival = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    images_by_color = Column(JSON, nullable=True)  # JSON object mapping colors to image lists
