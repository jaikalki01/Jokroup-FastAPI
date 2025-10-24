from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProductImageOut(BaseModel):
    id: int
    image_url: str

    class Config:
        orm_mode = True

class ProductColorOut(BaseModel):
    id: int
    color_name: str
    images: Optional[List[ProductImageOut]] = None

    class Config:
        orm_mode = True

class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    discount_price: Optional[float] = None
    category_id: Optional[int] = None         # <- make optional
    subcategory_id: Optional[int] = None      # <- make optional
    sizes: Optional[List[str]] = None
    in_stock: Optional[bool] = True
    rating: Optional[float] = 0.0
    reviews: Optional[int] = 0
    featured: Optional[bool] = False
    best_seller: Optional[bool] = False
    new_arrival: Optional[bool] = False
    highlights: Optional[str] = None
    specifications: Optional[str] = None
    details: Optional[str] = None
    created_at: Optional[datetime] = None

    product_colors: Optional[List[ProductColorOut]] = None

    class Config:
        orm_mode = True
