from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud
from app.models.order import Order, OrderTracking
from app.schemas import order as order_schema

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=order_schema.OrderOut)
def create_order(order: order_schema.OrderCreate, db: Session = Depends(get_db)):
    return crud.order.create_order(db, order)

@router.post("/{order_id}/tracking")
def add_tracking(order_id: int, status: str, message: str, db: Session = Depends(get_db)):
    update = crud.order.add_tracking_update(db, order_id, status, message)
    return {"detail": "Tracking updated", "data": update.status}

@router.get("/api/v1/product/{order_id}/tracking")
def get_order_tracking(order_id: str, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    tracking_updates = db.query(OrderTracking).filter(OrderTracking.order_id == db_order.id).all()

    tracking_data = {
        "order": db_order,
        "tracking": [
            {
                "id": update.id,
                "status": update.status,
                "message": update.message,
                "timestamp": update.timestamp.isoformat(),
            }
            for update in tracking_updates
        ],
    }

    return tracking_data
