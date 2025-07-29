from typing import Optional, List
from uuid import uuid4
from pydantic import BaseModel, Field, EmailStr, constr
from datetime import datetime

users = []

class UserCreate1(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class SuccessMessage(BaseModel):
    message: str

class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: str
    avatar: Optional[str] = None           # ✅ Now allows null
    created_at: Optional[datetime] = None  # ✅ Now allows null

    class Config:
        from_attributes = True


    class Config:
        from_attributes = True

class Address(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    postalCode: str
    country: str
    phone: str
    default: bool

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    role: str
    avatar: Optional[str] = "/placeholder.svg"
    addresses: Optional[List[Address]] = []
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class UserCreate(BaseModel):  # use this everywhere`
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class SuccessMessage(BaseModel):
    message: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

# For resetting password
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: constr(min_length=6)

# ✅ ADD THIS OUTSIDE, at the bottom:
class Token(BaseModel):
    access_token: str
    token_type: str

