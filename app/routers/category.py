import os
import shutil
from fileinput import filename
from typing import List
from fastapi import Request


from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form, File


from sqlalchemy.orm import Session
from sqlalchemy.testing import db

from app.database import get_db
from app import crud, models, schemas
from app.models import Category
from app.schemas import category as category_schema

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "static", "products")  # changed here
os.makedirs(UPLOAD_DIR, exist_ok=True)

def fix_image_url(image_path: str) -> str:
    """
    Convert stored image path to proper URL path.
    image_path expected like 'products/filename.jpg' or 'filename.jpg'
    """
    if not image_path:
        return ""
    image_path = image_path.lstrip("/")
    # Normalize URL to always start with /static/
    if image_path.startswith("products/"):
        return f"/static/{image_path}"
    else:
        return f"/static/products/{image_path}"

@router.post("/create", response_model=schemas.CategoryOut)
def create_category(
    name: str = Form(...),
    slug: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_ext = os.path.splitext(image.filename)[-1]
    file_name = f"{slug}{file_ext}"
    save_path = os.path.join(UPLOAD_DIR, file_name)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    # Save path relative to 'static' folder (because static is mounted at /static)
    image_path = f"/static/products/{filename}"

    new_category = models.Category(name=name, slug=slug, image=image_path)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return {
        "id": new_category.id,
        "name": new_category.name,
        "slug": new_category.slug,
        "image": fix_image_url(new_category.image),
        "subcategories": []
    }

@router.get("/list", response_model=List[schemas.CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    response = []
    for cat in categories:
        response.append({
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "image": fix_image_url(cat.image),
            "subcategories": [
                {
                    "id": sub.id,
                    "name": sub.name,
                    "slug": sub.slug,
                    "category_id": sub.category_id
                } for sub in cat.subcategories
            ]
        })
    return response

@router.put("/update/{category_id}", response_model=schemas.CategoryOut)
def update_category(
    category_id: int,
    name: str = Form(...),
    slug: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.name = name
    category.slug = slug

    if image:
        # Remove old image file
        if category.image:
            old_image_path = os.path.join(BASE_DIR, "..", "static", category.image.lstrip("/static/"))
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        # Save new image
        file_ext = os.path.splitext(image.filename)[-1]
        file_name = f"{slug}{file_ext}"
        save_path = os.path.join(UPLOAD_DIR, file_name)
        with open(save_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        category.image = f"...........  /{file_name}"

    db.commit()
    db.refresh(category)

    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "image": fix_image_url(category.image),
        "subcategories": [
            {
                "id": sub.id,
                "name": sub.name,
                "slug": sub.slug,
                "category_id": sub.category_id
            } for sub in category.subcategories
        ]
    }

@router.delete("/delete/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.image:
        image_path = os.path.join(BASE_DIR, "..", "static", category.image.lstrip("/static/"))
        if os.path.exists(image_path):
            os.remove(image_path)

    db.delete(category)
    db.commit()
    return {"detail": "Category deleted"}


# --- SUBCATEGORY ROUTES ---
@router.post("/subcategory/create", response_model=schemas.SubCategoryOut)
def create_subcategory(
    subcategory: schemas.SubCategoryCreate,
    db: Session = Depends(get_db)
):
    category = db.query(models.Category).filter(models.Category.id == subcategory.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    new_sub = models.SubCategory(**subcategory.dict())
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub

# Get All SubCategories
@router.get("/subcategory/list", response_model=List[schemas.SubCategoryOut])
def get_all_subcategories(db: Session = Depends(get_db)):
    return db.query(models.SubCategory).all()

# Update SubCategory
@router.put("/sub/update/{sub_id}", response_model=schemas.SubCategoryOut)
def update_subcategory(
    sub_id: int,
    sub_data: schemas.SubCategoryUpdate,
    db: Session = Depends(get_db)
):
    sub = db.query(models.SubCategory).filter(models.SubCategory.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="SubCategory not found")

    sub.name = sub_data.name
    sub.slug = sub_data.slug
    db.commit()
    db.refresh(sub)
    return sub

# Delete SubCategory
@router.delete("/sub/delete/{sub_id}")
def delete_subcategory(sub_id: int, db: Session = Depends(get_db)):
    sub = db.query(models.SubCategory).filter(models.SubCategory.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="SubCategory not found")

    db.delete(sub)
    db.commit()
    return {"detail": "SubCategory deleted"}