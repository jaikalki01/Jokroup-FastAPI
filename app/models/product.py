from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)#
    description = Column(Text)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, default=0.0)
    images = Column(Text)  # JSON string
    #images = Column(JSON)  # Use JSON type to store list of image URLs
    category_id = Column(String, nullable=False)  # Store category name directly
    subcategory_id = Column(String, nullable=False)  # Store subcategory name directly
    colors = Column(JSON)
    sizes = Column(JSON)  # JSON string
    in_stock = Column(Boolean, default=True)
    rating = Column(Float, default=0.0)
    reviews = Column(Integer, default=0)
    featured = Column(Boolean, default=False)
    best_seller = Column(Boolean, default=False)
    new_arrival = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    images_by_color = Column(Text, nullable=True)  # stores JSON: {"green": [...], "black": [...]}

    # Relationships

