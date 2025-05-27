from typing import List, Optional
from pydantic import BaseModel

class SubCategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    category_id: int

    class Config:
        orm_mode = True

class SubCategoryCreate(BaseModel):
    name: str
    slug: str
    category_id: int

class SubCategoryUpdate(BaseModel):
    name: str
    slug: str

class CategoryBase(BaseModel):
    name: str
    slug: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    image: Optional[str] = None
    subcategories: Optional[List[SubCategoryOut]] = []  # ✅ Make optional with default

    class Config:
        orm_mode = True
