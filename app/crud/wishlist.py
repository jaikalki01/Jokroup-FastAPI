from sqlalchemy.orm import Session
from app import models, schemas

def get_user_wishlist(db: Session, user_id: int):
    return db.query(models.WishlistItem).filter(models.WishlistItem.user_id == user_id).all()

def add_to_wishlist(db: Session, user_id: int, wishlist: schemas.WishlistCreate):
    db_item = models.WishlistItem(user_id=user_id, product_id=wishlist.product_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def remove_from_wishlist(db: Session, user_id: int, product_id: int):
    db_item = db.query(models.WishlistItem).filter_by(user_id=user_id, product_id=product_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False
