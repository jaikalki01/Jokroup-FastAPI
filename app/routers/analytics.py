from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Order, User

router = APIRouter(prefix="/api/admin/analytics", tags=["Admin Analytics"])

# ---------------- Admin Auth Placeholder ----------------
def get_current_admin_user():
    # Implement your auth here
    return True

# ---------------- Monthly Orders ----------------
@router.get("/monthly-orders")
def get_monthly_orders(db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    """
    Returns number of orders per month.
    """
    result = (
        db.query(
            func.date_format(Order.created_at, "%Y-%m").label("month"),
            func.count(Order.id).label("orders")
        )
        .group_by("month")
        .order_by("month")
        .all()
    )
    return [{"month": r.month, "orders": r.orders} for r in result]

# ---------------- Daily Orders (last 7 days) ----------------
@router.get("/daily-orders")
def get_daily_orders(db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    """
    Returns number of orders per day for the last 7 days.
    """
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    result = (
        db.query(
            func.date_format(Order.created_at, "%Y-%m-%d").label("day"),
            func.count(Order.id).label("orders")
        )
        .filter(Order.created_at >= seven_days_ago)
        .group_by("day")
        .order_by("day")
        .all()
    )
    return [{"day": r.day, "orders": r.orders} for r in result]

# ---------------- Top Customers ----------------
@router.get("/top-customers")
def get_top_customers(db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    """
    Returns top 10 customers based on number of orders.
    """
    result = (
        db.query(
            User.id,
            User.name,
            func.count(Order.id).label("orders")
        )
        .join(Order, Order.user_id == User.id)
        .group_by(User.id)
        .order_by(func.count(Order.id).desc())
        .limit(10)
        .all()
    )
    return [{"id": r.id, "name": r.name, "orders": r.orders} for r in result]
