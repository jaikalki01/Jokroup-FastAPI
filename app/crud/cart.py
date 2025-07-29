# app/crud/cart.py

from sqlalchemy.orm import Session
from app.models import CartItem
from app.schemas.cart import CartItemCreate, CartItemUpdate

def get_cart_items(db: Session, user_id: int):
    return db.query(CartItem).filter(CartItem.user_id == user_id).all()

def add_to_cart(db: Session, user_id: int, item: CartItemCreate):
    db_item = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.product_id == item.product_id
    ).first()

    if db_item:
        db_item.quantity += item.quantity
    else:
        db_item = CartItem(user_id=user_id, product_id=item.product_id, quantity=item.quantity)
        db.add(db_item)

    db.commit()
    db.refresh(db_item)
    return db_item

def update_cart_item(db: Session, item_id: int, update: CartItemUpdate):
    db_item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if db_item:
        db_item.quantity = update.quantity
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_cart_item(db: Session, item_id: int):
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()

def clear_cart(db: Session, user_id: int):
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
