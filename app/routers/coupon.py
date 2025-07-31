from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.schemas import coupon as coupon_schema
from app.authentication import get_current_admin_user  # ✅

router = APIRouter()

# ✅ Protected: Admin-only
@router.post("/", response_model=coupon_schema.CouponOut)
def create_coupon(
    coupon: coupon_schema.CouponCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin_user)  # 🔐
):
    db_coupon = crud.coupon.get_coupon_by_code(db, code=coupon.code)
    if db_coupon:
        raise HTTPException(status_code=400, detail="Coupon code already exists.")
    return crud.coupon.create_coupon(db, coupon=coupon)

# ✅ Public: Anyone can read coupons
@router.get("/", response_model=list[coupon_schema.CouponOut])
def read_coupon(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.coupon.get_coupon(db, skip=skip, limit=limit)

# ✅ Protected: Admin-only
@router.put("/{coupon_id}", response_model=coupon_schema.CouponOut)
def update_coupon(
    coupon_id: int,
    coupon_update: coupon_schema.CouponUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin_user)  # 🔐
):
    db_coupon = crud.coupon.get_coupon_by_id(db, coupon_id=coupon_id)
    if not db_coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")

    return crud.coupon.update_coupon(db, db_coupon=db_coupon, coupon_update=coupon_update)

# ✅ Protected: Admin-only
@router.delete("/{coupon_id}", response_model=coupon_schema.CouponOut)
def delete_coupon(
    coupon_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin_user)  # 🔐
):
    db_coupon = crud.coupon.get_coupon_by_id(db, coupon_id=coupon_id)
    if not db_coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")

    crud.coupon.delete_coupon(db, db_coupon=db_coupon)
    return db_coupon
