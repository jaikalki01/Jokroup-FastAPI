from fastapi import APIRouter, Depends, HTTPException, Form
from pydantic_core.core_schema import model_schema
from sqlalchemy.orm import Session

from app.authentication import verify_password, create_access_token, get_current_user
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


@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, email=email)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
@router.get("/me", response_model=user_schema.UserOut)
def get_current_user_info(
    user: User = Depends(get_current_user)
):
    return user