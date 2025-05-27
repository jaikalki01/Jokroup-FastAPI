from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

# Shared properties
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    discount_price: Optional[float] = 0.0
    images: List[str]
    category_id: Optional[int] = None  # Changed from category_id to category_name
    subcategory_id: Optional[int] = None  # Changed from subcategory_id to subcategory_name
    colors: List[str]
    sizes: List[str]
    in_stock: bool = True
    rating: Optional[float] = 0.0
    reviews: Optional[int] = 0
    featured: bool = False
    best_seller: bool = False
    new_arrival: bool = False


# For creating a product
class ProductCreate(ProductBase):
    pass


# For outputting a product to the client
class ProductOut(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
