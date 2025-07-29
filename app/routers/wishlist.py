from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.authentication import get_db, get_current_user
from app.schemas.wishlist import WishlistCreate, WishlistItemOut

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

@router.get("/", response_model=list[schemas.WishlistItemOut])
def get_wishlist(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.wishlist.get_user_wishlist(db, current_user.id)

@router.post("/", response_model=schemas.WishlistItemOut)
def add_wishlist_item(wishlist: schemas.WishlistCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.wishlist.add_to_wishlist(db, current_user.id, wishlist)

@router.delete("/{product_id}")
def delete_wishlist_item(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    success = crud.wishlist.remove_from_wishlist(db, current_user.id, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found in wishlist")
    return {"detail": "Item removed"}
