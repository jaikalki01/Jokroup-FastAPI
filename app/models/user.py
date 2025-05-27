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
    role = Column(String(250))
    avatar = Column(String(250), nullable=True)
    created_at = Column(DateTime)
    addresses = relationship("Address", back_populates="user")

    settings = relationship("UserSettings", back_populates="user")

orders = relationship("Order", back_populates="user")



# user setting




class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    email = Column(Boolean, default=True)
    offers = Column(Boolean, default=True)
    updates = Column(Boolean, default=True)

    user = relationship("User", back_populates="settings")

