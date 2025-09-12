from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    discount_price: Optional[float] = 0.0
    images: List[str]  # List of image URLs
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None

    sizes: List[str]   # List of size strings
    colors: List[str]  # List of color strings
    in_stock: bool = True
    rating: Optional[float] = 0.0
    reviews: Optional[int] = 0
    featured: bool
    best_seller: bool
    new_arrival: bool
    images_by_color: Optional[Dict[str, List[str]]] = None  # Optional mapping colors to image URLs

    highlights: Optional[List[str]]
    specifications: Optional[Dict[str, str]]
    details: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
