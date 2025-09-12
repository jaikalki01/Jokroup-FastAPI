# models/product.py
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, default=0.0)
    images = Column(JSON)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=False)
    colors = Column(JSON)
    sizes = Column(JSON)
    in_stock = Column(Boolean, default=True)
    rating = Column(Float, default=0.0)
    reviews = Column(Integer, default=0)
    featured = Column(Boolean, default=False)
    best_seller = Column(Boolean, default=False)
    new_arrival = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    highlights = Column(Text, nullable=True)
    specifications = Column(Text, nullable=True)
    details = Column(Text, nullable=True)

    category = relationship("Category", back_populates="products")
    subcategory = relationship("SubCategory", back_populates="products")
