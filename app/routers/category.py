from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form, File
from sqlalchemy.orm import Session
import os, shutil
from typing import List

from app.database import get_db
from app import models, schemas
from app.models import Category
from app.schemas import category as category_schema
from app.authentication import get_current_admin_user # ✅ Your auth logic

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "static", "products")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def fix_image_url(image_path: str) -> str:
    if not image_path:
        return ""
    image_path = image_path.lstrip("/")
    if image_path.startswith("products/"):
        return f"/static/{image_path}"
    else:
        return f"/static/products/{image_path}"

# ✅ Admin Protected
@router.post("/create", response_model=schemas.CategoryOut)
def create_category(
    name: str = Form(...),
    slug: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin_user)  # ✅
):
    file_ext = os.path.splitext(image.filename)[-1]
    file_name = f"{slug}{file_ext}"
    save_path = os.path.join(UPLOAD_DIR, file_name)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(image.file, f)

    image_path = f"products/{file_name}"
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

# ✅ Public
@router.get("/list", response_model=List[schemas.CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    response = []

    for cat in categories:
        # Get subcategories cleanly
        subcats = [
            {
                "id": sub.id,
                "name": sub.name or "Unnamed",
                "slug": sub.slug,
                "category_id": sub.category_id,
                "subcategory_id": sub.id
            }
            for sub in cat.subcategories
        ]

        response.append({
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "image": fix_image_url(cat.image),
            "subcategories": subcats or None
        })

    return response




# ✅ Admin Protected
@router.put("/update/{category_id}", response_model=schemas.CategoryOut)
def update_category(
    category_id: int,
    name: str = Form(...),
    slug: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin_user)  # ✅
):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.name = name
    category.slug = slug

    if image:
        if category.image:
            old_image_path = os.path.join(BASE_DIR, "..", "static", category.image.lstrip("/static/"))
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        file_ext = os.path.splitext(image.filename)[-1]
        file_name = f"{slug}{file_ext}"
        save_path = os.path.join(UPLOAD_DIR, file_name)
        with open(save_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        category.image = f"products/{file_name}"

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

# ✅ Admin Protected
@router.delete("/delete/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin_user)  # ✅
):
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

# ✅ Admin Protected
@router.post("/subcategory/create", response_model=schemas.SubcategoryOut)
def create_subcategory(
    subcategory: schemas.SubCategoryCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin_user)
):
    category = db.query(models.Category).filter(models.Category.id == subcategory.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    new_sub = models.SubCategory(**subcategory.dict())
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)

    return {
        "id": new_sub.id,
        "name": new_sub.name,
        "slug": new_sub.slug,
        "category_id": new_sub.category_id,
        "subcategory_id": new_sub.id
    }


# ✅ Public
@router.get("/subcategory/list", response_model=List[schemas.SubcategoryOut])
def get_all_subcategories(db: Session = Depends(get_db)):
    subs = db.query(models.SubCategory).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "slug": s.slug,
            "category_id": s.category_id,
            "subcategory_id": s.id
        } for s in subs
    ]


# ✅ Admin Protected
@router.put("/sub/update/{sub_id}", response_model=schemas.SubcategoryOut)
def update_subcategory(
    sub_id: int,
    sub_data: schemas.SubCategoryUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin_user)
):
    sub = db.query(models.SubCategory).filter(models.SubCategory.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="SubCategory not found")

    sub.name = sub_data.name
    sub.slug = sub_data.slug
    db.commit()
    db.refresh(sub)
    return {
        "id": sub.id,
        "name": sub.name,
        "slug": sub.slug,
        "category_id": sub.category_id,
        "subcategory_id": sub.id
    }


# ✅ Admin Protected
@router.delete("/sub/delete/{sub_id}")
def delete_subcategory(
    sub_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin_user)  # ✅
):
    sub = db.query(models.SubCategory).filter(models.SubCategory.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="SubCategory not found")

    db.delete(sub)
    db.commit()
    return {"detail": "SubCategory deleted"}
