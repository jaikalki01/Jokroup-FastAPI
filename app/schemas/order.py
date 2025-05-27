from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class TrackingUpdate(BaseModel):
    status: str
    message: str
    timestamp: datetime

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    user_id: int

class OrderCreate(OrderBase):
    pass

class OrderOut(OrderBase):
    id: int
    status: str
    created_at: datetime
    tracking_updates: List[TrackingUpdate] = []

    class Config:
        orm_mode = True
