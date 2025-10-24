from typing import List
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.models import User
from app.mail import send_reset_email
from app.authentication import (
    get_current_user,
    get_current_admin_user,
    get_password_hash,
    verify_password,   # ✅ moved from correct source
    SECRET_KEY,
    ALGORITHM,
    create_access_token,
)
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
    # Check if email already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password,
        phone=user.phone,
        address_line1=user.address_line1,
        address_line2=user.address_line2,
        city=user.city,
        region=user.region,
        postal_code=user.postal_code,
        country=user.country,
        created_at=datetime.utcnow(),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Registration successful"}




# -------------------- LOGIN --------------------
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # ✅ Include role in token payload
    access_token = create_access_token(data={"sub": user.email, "role": user.role})

    return {"access_token": access_token, "token_type": "bearer"}


# -------------------- GET CURRENT USER --------------------
@router.get("/me", response_model=UserOut)
def get_current_user_data(current_user: User = Depends(get_current_user)):
    return current_user


# -------------------- GET ALL USERS (Admin only) --------------------
@router.get("/users", response_model=List[UserOut])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    return db.query(User).all()


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
@router.post("/forgot-password", response_model=SuccessMessage)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, request.email)
    if not user:
        # Return generic message for security
        return {"message": "If this email exists, a reset link has been sent."}

    reset_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=15),
    )

    reset_link = f"http://localhost:8080/reset-password?token={reset_token}"
    send_reset_email(user.email, reset_link)
    print(f"[DEBUG] Password reset link: {reset_link}")

    return {"message": "If this email exists, a reset link has been sent."}


# -------------------- RESET PASSWORD --------------------
@router.post("/reset-password", response_model=SuccessMessage)
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

    return {"message": "Password reset successful"}
