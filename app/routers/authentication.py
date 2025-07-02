from fastapi import APIRouter, Depends, HTTPException, Form
from pydantic_core.core_schema import model_schema
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import user as user_schema
from app.crud import user as crud
from app.schemas.user import SuccessMessage
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()


import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"  # Use environment variables in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 160

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

from pydantic import BaseModel
from datetime import datetime

class LoginRequest(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: str
    avatar: str
    created_at: datetime

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    user: UserOut
    token: str


@router.post("/login")
def login(
    email: str = Form(...),  # OAuth2 expects `username`
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_email(db, email=email)
    if not db_user or not verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(data={"sub": db_user.email, "role": db_user.role})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


