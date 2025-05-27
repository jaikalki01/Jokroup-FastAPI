from fastapi import APIRouter, Depends, HTTPException
from pydantic_core.core_schema import model_schema
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import user as user_schema
from app.crud import user as crud

router = APIRouter()

@router.post("/signUp", response_model=user_schema.UserOut)
def create_admin(user: user_schema.UserCreate1, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user1(db=db, user=user)


