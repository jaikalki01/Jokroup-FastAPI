from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # ✅ Fix added here
    status = Column(String(50), default="processing")
    created_at = Column(DateTime, default=datetime.utcnow)

    tracking_updates = relationship("OrderTracking", back_populates="order")
    user = relationship("User", back_populates="orders")  # ✅ Add this line


class OrderTracking(Base):
    __tablename__ = "order_tracking"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    status = Column(String(50))
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="tracking_updates")
