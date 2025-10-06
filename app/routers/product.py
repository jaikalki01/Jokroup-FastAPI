from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import os, json

from app.database import get_db
from app.models import User
from app.models.product import Product, ProductColor, ProductImage
from app.schemas.product import ProductOut
from app.authentication import get_current_admin_user


router = APIRouter()

import re
from fastapi import Request, UploadFile
import shutil

# Where uploaded images will be stored
UPLOAD_DIR = "static/uploads/products"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def slugify(value: str) -> str:
    """Convert 'Red Shirt' -> 'red_shirt' (safe for filenames/keys)."""
    value = value.lower()
    value = re.sub(r'[^a-z0-9]+', '_', value)
    return value.strip("_")


def save_upload_file(upload_file: UploadFile, destination_folder: str) -> str:
    """Save an uploaded file to disk and return relative filename."""
    filename = f"{slugify(str(int(__import__('time').time()*1000)))}_{upload_file.filename}"
    file_path = os.path.join(destination_folder, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return filename  # we store just filename, not full path


def make_file_url(request: Request, filename: str) -> str:
    """Build a full URL for a stored static file."""
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}/static/uploads/products/{filename}"


# ---------------------------- PUBLIC ROUTES ----------------------------
@router.get("/list", response_model=List[ProductOut])
def list_products(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).all()
    for p in products:
        for c in p.product_colors:
            for img in c.images:
                img.image_url = make_file_url(request, img.image_url)
    return products


@router.get("/product/{product_id}", response_model=ProductOut)
def get_product(product_id: int, request: Request, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for c in product.product_colors:
        for img in c.images:
            img.image_url = make_file_url(request, img.image_url)
    return product


# ---------------------------- ADMIN ROUTES ----------------------------
# helper: permissive list parser
def parse_list_field(field):
    """
    Accepts:
      - a Python list (returns as-is)
      - a JSON array string like '["Red","Blue"]'
      - a comma-separated string like 'Red,Blue'
      - None/empty -> returns []
    """
    if not field:
        return []

    if isinstance(field, list):
        return field

    # try JSON first
    try:
        parsed = json.loads(field)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, str):
            return [parsed]
    except Exception:
        pass

    # fallback: comma-separated
    if isinstance(field, str):
        return [s.strip() for s in field.split(",") if s.strip()]

    return []

# ---------------- CREATE ----------------
@router.post("/create")
async def create_product(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    discount_price: float = Form(0.0),
    category_id: int = Form(...),
    subcategory_id: int = Form(...),
    colors: str = Form(...),  # accepts JSON array or comma-separated
    sizes: Optional[str] = Form(None),
    highlights: Optional[str] = Form(None),
    specifications: Optional[str] = Form(None),
    details: Optional[str] = Form(None),
    featured: bool = Form(False),
    best_seller: bool = Form(False),
    new_arrival: bool = Form(False),

    # ensures Swagger shows multipart/form-data
    dummy_image: Optional[UploadFile] = File(None),

    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    # parse lists permissively
    colors_list = parse_list_field(colors)
    if not isinstance(colors_list, list):
        raise HTTPException(status_code=400, detail="`colors` must be a list or JSON array or comma-separated string")

    sizes_val = parse_list_field(sizes)

    # create product
    product = Product(
        name=name,
        description=description,
        price=price,
        discount_price=discount_price,
        category_id=category_id,
        subcategory_id=subcategory_id,
        sizes=sizes_val,
        highlights=highlights,
        specifications=specifications,
        details=details,
        featured=featured,
        best_seller=best_seller,
        new_arrival=new_arrival,
    )
    db.add(product)
    db.flush()  # to get product.id

    # create color rows and build map slug->color_id
    color_map = {}
    for color in colors_list:
        pc = ProductColor(product_id=product.id, color_name=color)
        db.add(pc)
        db.flush()
        color_map[slugify(color)] = pc.id

    # process uploaded files dynamically from form
    form = await request.form()
    for key, value in form.multi_items():
        if key.startswith("images_") and hasattr(value, "filename"):
            slug = key[len("images_"):]
            if slug not in color_map:
                # skip unexpected color keys
                continue
            filename = save_upload_file(value, UPLOAD_DIR)
            pi = ProductImage(color_id=color_map[slug], image_url=filename)
            db.add(pi)

    db.commit()
    db.refresh(product)
    return {"message": "Product created successfully!", "product_id": product.id}


# ---------------- UPDATE ----------------
@router.put("/update/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    request: Request,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    discount_price: Optional[float] = Form(None),
    category_id: Optional[int] = Form(None),
    subcategory_id: Optional[int] = Form(None),
    colors: Optional[str] = Form(None),  # to add new colors (JSON or comma-separated)
    sizes: Optional[str] = Form(None),
    highlights: Optional[str] = Form(None),
    specifications: Optional[str] = Form(None),
    details: Optional[str] = Form(None),
    featured: Optional[bool] = Form(None),
    best_seller: Optional[bool] = Form(None),
    new_arrival: Optional[bool] = Form(None),

    # ensures Swagger shows multipart/form-data
    dummy_image: Optional[UploadFile] = File(None),

    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # update scalar fields when provided
    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if price is not None:
        product.price = price
    if discount_price is not None:
        product.discount_price = discount_price
    if category_id is not None:
        product.category_id = category_id
    if subcategory_id is not None:
        product.subcategory_id = subcategory_id

    if sizes is not None:
        product.sizes = parse_list_field(sizes)

    if highlights is not None:
        product.highlights = highlights
    if specifications is not None:
        product.specifications = specifications
    if details is not None:
        product.details = details
    if featured is not None:
        product.featured = featured
    if best_seller is not None:
        product.best_seller = best_seller
    if new_arrival is not None:
        product.new_arrival = new_arrival

    # handle adding new colors (we won't auto-delete existing colors here)
    new_color_map = {}
    if colors:
        colors_list = parse_list_field(colors)
        if not isinstance(colors_list, list):
            raise HTTPException(status_code=400, detail="`colors` must be a list or JSON array or comma-separated string")

        existing_names = {c.color_name.lower(): c for c in product.product_colors}
        for c in colors_list:
            if c.lower() not in existing_names:
                pc = ProductColor(product_id=product.id, color_name=c)
                db.add(pc)
                db.flush()
                new_color_map[slugify(c)] = pc.id

    # process uploaded files dynamically
    form = await request.form()
    for key, value in form.multi_items():
        if key.startswith("images_") and hasattr(value, "filename"):
            slug = key[len("images_"):]
            # find existing color by slug
            target_color = None
            for pc in product.product_colors:
                if slugify(pc.color_name) == slug:
                    target_color = pc
                    break
            # if not found, check newly created colors in this request
            if not target_color and slug in new_color_map:
                target_color = db.query(ProductColor).filter_by(id=new_color_map[slug]).first()
            if not target_color:
                # skip unknown color key
                continue
            filename = save_upload_file(value, UPLOAD_DIR)
            pi = ProductImage(color_id=target_color.id, image_url=filename)
            db.add(pi)

    db.commit()
    db.refresh(product)

    # convert image filenames to full URLs before returning (optional, router elsewhere may already do this)
    for c in product.product_colors:
        for img in c.images:
            img.image_url = make_file_url(request, img.image_url)

    return product

@router.delete("/image/{image_id}")
def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_admin_user),  # 🔒 ADMIN ONLY
    db: Session = Depends(get_db),
):
    img = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")

    # try deleting file from disk
    try:
        path = os.path.join(UPLOAD_DIR, img.image_url)
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

    db.delete(img)
    db.commit()

    return {"message": f"Image {image_id} deleted successfully!"}
