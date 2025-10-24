from pydantic import BaseModel, ConfigDict

class WishlistBase(BaseModel):
    product_id: int

class WishlistCreate(WishlistBase):
    pass

class WishlistItemOut(BaseModel):
    id: int
    product_id: int

    # ✅ New Pydantic v2 syntax (replaces class Config)
    model_config = ConfigDict(from_attributes=True)
