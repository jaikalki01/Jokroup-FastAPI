from pydantic import BaseModel

class WishlistBase(BaseModel):
    product_id: int

class WishlistCreate(WishlistBase):
    pass

class WishlistItemOut(BaseModel):
    id: int
    product_id: int

    class Config:
        orm_mode = True
