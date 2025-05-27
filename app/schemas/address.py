from pydantic import BaseModel
from typing import Optional

class AddressBase(BaseModel):
    name: str
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    phone: str
    default: Optional[bool] = False
    user_id: int

class AddressCreate(AddressBase):
    pass  # same as AddressBase for now

class AddressOut(AddressBase):
    id: int

    class Config:
        from_attributes = True
