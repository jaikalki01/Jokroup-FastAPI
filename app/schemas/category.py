from typing import List, Optional
from pydantic import BaseModel

class SubcategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    category_id: Optional[int]  # <-- allow None
    subcategory_id: Optional[int]  # <-- allow None

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
    # avoid mutable default; allow None when there are no subcategories
    subcategories: Optional[List[SubcategoryOut]] = None

    class Config:
        orm_mode = True
