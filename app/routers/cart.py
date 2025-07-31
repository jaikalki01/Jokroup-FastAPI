# app/router/cart.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.cart import CartItem
from app.schemas.cart import CartItemCreate, CartItemOut, CartItemUpdate
from app.crud import cart as cart_crud
from app.database import get_db
from app.authentication import get_current_user
from app.models import User

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/", response_model=List[CartItemOut])
def get_cart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return cart_crud.get_cart_items(db, user.id)

@router.post("/", response_model=CartItemOut)
def add_item(item: CartItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return cart_crud.add_to_cart(db, user.id, item)

@router.put("/{item_id}", response_model=CartItemOut)
def update_item(item_id: int, update: CartItemUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart_item = cart_crud.update_cart_item(db, item_id, update)
    if not cart_item or cart_item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Item not found or not authorized")
    return cart_item

@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not cart_item or cart_item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Item not found or not authorized")
    cart_crud.delete_cart_item(db, item_id)
    return {"message": "Item removed"}

@router.delete("/clear")
def clear_user_cart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart_crud.clear_cart(db, user.id)
    return {"message": "Cart cleared"}
