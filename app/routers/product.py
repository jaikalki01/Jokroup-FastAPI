from datetime import datetime, timedelta

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union
import json
import os
import time

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductOut

router = APIRouter()

# Helper to parse JSON list fields or comma-separated strings
def safe_parse_list_field(field):
    if not field:
        return []
    if isinstance(field, list):
        return field
    try:
        parsed = json.loads(field)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, str):
            return [parsed]
    except Exception:
        if isinstance(field, str):
            return [item.strip() for item in field.split(",") if item.strip()]
    return []


@router.post("/create-new-arrival")
async def create_new_arrival_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    discount_price: float = Form(0),
    category_id: str = Form(...),
    subcategory_id: str = Form(...),
    colors: str = Form(...),
    sizes: str = Form(...),
    in_stock: bool = Form(True),
    rating: float = Form(0.0),
    reviews: int = Form(0),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    upload_folder = "static/products"
    os.makedirs(upload_folder, exist_ok=True)

    image_paths = []
    for image in images:
        filename = f"{time.time()}_{image.filename}"
        file_path = os.path.join(upload_folder, filename)
        with open(file_path, "wb") as f:
            f.write(await image.read())
        image_paths.append(f"/static/products/{filename}")

    color_list = safe_parse_list_field(colors)
    size_list = safe_parse_list_field(sizes)

    new_product = Product(
        name=name,
        description=description,
        price=price,
        discount_price=discount_price,
        images=json.dumps(image_paths),
        category_id=category_id,
        subcategory_id=subcategory_id,
        colors=json.dumps(color_list),
        sizes=json.dumps(size_list),
        in_stock=in_stock,
        rating=rating,
        reviews=reviews,
        featured=False,
        best_seller=False,
        new_arrival=True,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {"message": "New Arrival product created successfully!", "product_id": new_product.id}



@router.get("/new-arrivals")
def get_new_arrivals(db: Session = Depends(get_db)):
    new_arrivals = db.query(Product).filter(Product.new_arrival == True).all()

    results = []
    for p in new_arrivals:
        results.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "discount_price": p.discount_price,
            "images": json.loads(p.images) if isinstance(p.images, str) else p.images,
        })
    return results


# ---------------------------- CREATE PRODUCT ----------------------------
@router.post("/create")
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    discount_price: float = Form(0),
    category_id: str = Form(...),
    subcategory_id: str = Form(...),
    colors: str = Form(...),
    sizes: str = Form(...),
    in_stock: bool = Form(True),
    rating: float = Form(0.0),
    reviews: int = Form(0),
    featured: bool = Form(False),
    best_seller: bool = Form(False),
    new_arrival: bool = Form(False),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    upload_folder = "staticstatic/products"
    os.makedirs(upload_folder, exist_ok=True)

    image_paths = []
    for image in images:
        filename = f"{time.time()}_{image.filename}"
        file_path = os.path.join(upload_folder, filename)
        try:
            with open(file_path, "wb") as f:
                f.write(await image.read())
            image_paths.append(f"/static/products/{filename}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

    color_list = safe_parse_list_field(colors)
    size_list = safe_parse_list_field(sizes)

    new_product = Product(
        name=name,
        description=description,
        price=price,
        discount_price=discount_price,
        images=json.dumps(image_paths),
        category_id=category_id,
        subcategory_id=subcategory_id,
        colors=json.dumps(color_list),
        sizes=json.dumps(size_list),
        in_stock=in_stock,
        rating=rating,
        reviews=reviews,
        featured=featured,
        best_seller=best_seller,
        new_arrival=new_arrival,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {"message": "Product created successfully!", "product_id": new_product.id}

# ---------------------------- LIST PRODUCTS ----------------------------
@router.get("/list", response_model=List[ProductOut])
async def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    for product in products:
        product.colors = safe_parse_list_field(product.colors)
        product.sizes = safe_parse_list_field(product.sizes)
        product.images = safe_parse_list_field(product.images)
    return products

# ---------------------------- GET SINGLE PRODUCT ----------------------------
@router.get("/product/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.colors = safe_parse_list_field(product.colors)
    product.sizes = safe_parse_list_field(product.sizes)
    product.images = safe_parse_list_field(product.images)
    return product

# ---------------------------- UPDATE PRODUCT ----------------------------
@router.put("/update/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    name: Union[str, None] = Form(None),
    description: Union[str, None] = Form(None),
    price: Union[float, None] = Form(None),
    discount_price: Union[float, None] = Form(None),
    category_id: Union[str, None] = Form(None),
    subcategory_id: Union[str, None] = Form(None),
    colors: Union[str, None] = Form(None),
    sizes: Union[str, None] = Form(None),
    in_stock: Union[bool, None] = Form(None),
    rating: Union[float, None] = Form(None),
    reviews: Union[int, None] = Form(None),
    featured: Union[bool, None] = Form(None),
    best_seller: Union[bool, None] = Form(None),
    new_arrival: Union[bool, None] = Form(None),
    images: Union[List[UploadFile], None] = File(None),
    db: Session = Depends(get_db)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if name is not None:
        db_product.name = name
    if description is not None:
        db_product.description = description
    if price is not None:
        db_product.price = price
    if discount_price is not None:
        db_product.discount_price = discount_price
    if category_id is not None:
        db_product.category_id = category_id
    if subcategory_id is not None:
        db_product.subcategory_id = subcategory_id
    if colors is not None:
        db_product.colors = json.dumps(safe_parse_list_field(colors))
    if sizes is not None:
        db_product.sizes = json.dumps(safe_parse_list_field(sizes))
    if in_stock is not None:
        db_product.in_stock = in_stock
    if rating is not None:
        db_product.rating = rating
    if reviews is not None:
        db_product.reviews = reviews
    if featured is not None:
        db_product.featured = featured
    if best_seller is not None:
        db_product.best_seller = best_seller
    if new_arrival is not None:
        db_product.new_arrival = new_arrival

    if images is not None:
        upload_folder = "staticstatic/products"
        os.makedirs(upload_folder, exist_ok=True)

        image_paths = []
        for image in images:
            filename = f"{time.time()}_{image.filename}"
            file_path = os.path.join(upload_folder, filename)
            with open(file_path, "wb") as f:
                f.write(await image.read())
            image_paths.append(f"/static/products/{filename}")
        db_product.images = json.dumps(image_paths)

    db.commit()
    db.refresh(db_product)

    db_product.colors = safe_parse_list_field(db_product.colors)
    db_product.sizes = safe_parse_list_field(db_product.sizes)
    db_product.images = safe_parse_list_field(db_product.images)

    return db_product

# ---------------------------- DELETE PRODUCT ----------------------------
@router.delete("/delete/{product_id}", response_model=ProductOut)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()

    db_product.colors = safe_parse_list_field(db_product.colors)
    db_product.sizes = safe_parse_list_field(db_product.sizes)
    db_product.images = safe_parse_list_field(db_product.images)

    return db_product
