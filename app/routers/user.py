from typing import List
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.mail import send_reset_email
from app.security import hash_password, verify_password
from app.authentication import (
    get_current_user,
    get_current_admin_user,
    get_password_hash,
    SECRET_KEY,
    ALGORITHM,
    create_access_token,
)
from app.schemas import user as user_schema
from app.schemas.user import (
    UserOut,
    UserCreate1,
    Token,
    ChangePasswordRequest,
    SuccessMessage,
    ResetPasswordRequest,
    ForgotPasswordRequest,
)
from app.crud import user as crud

router = APIRouter()


# -------------------- SIGN UP --------------------
@router.post("/signUp", response_model=SuccessMessage)
def create_user(user: UserCreate1, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    crud.create_user1(db=db, user=user)
    return {"message": "Registration successful"}


# -------------------- LOGIN --------------------
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# -------------------- GET ALL USERS --------------------
@router.get("/users", response_model=List[UserOut])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return db.query(User).all()


# -------------------- GET CURRENT USER --------------------
@router.get("/me")
def get_current_user_data(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "name": current_user.name if hasattr(current_user, "name") else "",
    }


# -------------------- GET USER BY ID --------------------
@router.get("/{user_id}", response_model=UserOut)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# -------------------- UPDATE USER --------------------


# -------------------- CHANGE PASSWORD --------------------
@router.post("/change-password", response_model=SuccessMessage)
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    current_user.password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


# -------------------- FORGOT PASSWORD --------------------
@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, request.email)
    if not user:
        return {"msg": "If this email exists, a reset link has been sent."}
    reset_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=15),
    )
    reset_link = f"http://localhost:8080/reset-password?token={reset_token}"
    send_reset_email(user.email, reset_link)
    print(f"[DEBUG] Reset link: {reset_link}")
    return {"msg": "If this email exists, a reset link has been sent."}


# -------------------- RESET PASSWORD --------------------
@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401, detail="Invalid or expired token"
    )
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, email)
    if not user:
        raise credentials_exception

    user.password = get_password_hash(request.new_password)
    db.commit()
    return {"msg": "Password reset successful"}
