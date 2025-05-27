from fastapi import APIRouter, Depends, HTTPException
from pydantic_core.core_schema import model_schema
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import user as user_schema
from app.crud import user as crud
from app.schemas.user import SuccessMessage

router = APIRouter()



@router.post("/signUp",response_model=SuccessMessage)
def create_user(user: user_schema.UserCreate1, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    crud.create_user1(db=db, user=user)
    return {"message": "Registration successful"}


@router.get("/{user_id}", response_model=user_schema.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


