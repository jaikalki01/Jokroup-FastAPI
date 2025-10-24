from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(250))
    last_name = Column(String(250))
    email = Column(String(250), unique=True, index=True)
    password = Column(String(250))
    role = Column(String(250), default="user")
    avatar = Column(String(250), nullable=True)
    phone = Column(String(50), nullable=True)  # new field
    address_line1 = Column(String(250), nullable=True)  # new field
    address_line2 = Column(String(250), nullable=True)  # new field
    city = Column(String(100), nullable=True)  # new field
    region = Column(String(100), nullable=True)  # new field
    postal_code = Column(String(20), nullable=True)  # new field
    country = Column(String(100), nullable=True)  # new field
    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ All relationships must be indented properly within the class
    addresses = relationship("Address", back_populates="user")
    settings = relationship("UserSettings", back_populates="user")
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete")
    wishlist_items = relationship("WishlistItem", back_populates="user", cascade="all, delete")



# user setting




class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    email = Column(Boolean, default=True)
    offers = Column(Boolean, default=True)
    updates = Column(Boolean, default=True)

    user = relationship("User", back_populates="settings")

