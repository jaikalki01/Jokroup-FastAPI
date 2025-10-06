from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ---------------- IMAGE ----------------
class ProductImageOut(BaseModel):
    id: int
    image_url: str

    class Config:
        orm_mode = True  # tells Pydantic to work with SQLAlchemy objects


# ---------------- COLOR ----------------
class ProductColorOut(BaseModel):
    id: int
    color_name: str
    images: List[ProductImageOut] = []  # nested images

    class Config:
        orm_mode = True


# ---------------- PRODUCT ----------------
class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    discount_price: Optional[float] = None
    category_id: int
    subcategory_id: int
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
    created_at: Optional[datetime]

    # ✅ Nested colors (and inside that, nested images)
    product_colors: List[ProductColorOut] = []

    class Config:
        orm_mode = True
