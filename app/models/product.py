# app/models/product.py
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, default=0.0)

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=False)

    # JSON fields (still okay for simple lists)
    sizes = Column(JSON, nullable=True)

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

    # Relationships
    category = relationship("Category", back_populates="products")
    subcategory = relationship("SubCategory", back_populates="products")
    product_colors = relationship("ProductColor", back_populates="product", cascade="all, delete-orphan")


class ProductColor(Base):
    __tablename__ = "product_colors"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    color_name = Column(String(50), nullable=False)

    product = relationship("Product", back_populates="product_colors")
    images = relationship("ProductImage", back_populates="color", cascade="all, delete-orphan")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    color_id = Column(Integer, ForeignKey("product_colors.id", ondelete="CASCADE"))
    image_url = Column(String(255), nullable=False)

    color = relationship("ProductColor", back_populates="images")
