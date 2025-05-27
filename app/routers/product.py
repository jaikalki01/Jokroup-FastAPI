from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from typing import List
import json
import os
import time

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductOut
from fastapi.exceptions import HTTPException

router = APIRouter()

# Create Product
@router.post("/create")
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    discount_price: float = Form(0),
    category_id: str = Form(...),
    subcategory_id: str = Form(...),
    colors: str = Form(...),     # Expecting: "red,blue,green"
    sizes: str = Form(...),      # Expecting: "S,M,L"
    in_stock: bool = Form(True),
    rating: float = Form(0.0),
    reviews: int = Form(0),
    featured: bool = Form(False),
    best_seller: bool = Form(False),
    new_arrival: bool = Form(False),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    upload_folder = "static/products"
    os.makedirs(upload_folder, exist_ok=True)

    # Save images and collect paths
    image_paths = []
    for image in images:
        filename = f"{time.time()}_{image.filename}"
        file_path = os.path.join(upload_folder, filename)

        try:
            with open(file_path, "wb") as f:
                f.write(await image.read())
            image_paths.append(f"/static/products/{filename}")  # Correct path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

    # Parse colors and sizes safely
    try:
        color_list = json.loads(colors) if isinstance(colors, str) else []
    except json.JSONDecodeError:
        color_list = [c.strip() for c in colors.split(",")] if isinstance(colors, str) else []
    try:
        size_list = json.loads(sizes) if isinstance(sizes, str) else []
    except json.JSONDecodeError:
        size_list = [s.strip() for s in sizes.split(",")] if isinstance(sizes, str) else []

    new_product = Product(
        name=name,
        description=description,
        price=price,
        discount_price=discount_price,
        images=json.dumps(image_paths),   # Store as JSON string
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

# List Products
@router.get("/list")
async def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found")

    result = []
    for p in products:
        # Safely load JSON fields only if they are strings
        images = []
        if isinstance(p.images, str):
            try:
                images = json.loads(p.images)
            except json.JSONDecodeError:
                images = []
        elif isinstance(p.images, list):
            images = p.images

        colors = []
        if isinstance(p.colors, str):
            try:
                colors = json.loads(p.colors)
            except json.JSONDecodeError:
                colors = []
        elif isinstance(p.colors, list):
            colors = p.colors

        sizes = []
        if isinstance(p.sizes, str):
            try:
                sizes = json.loads(p.sizes)
            except json.JSONDecodeError:
                sizes = []
        elif isinstance(p.sizes, list):
            sizes = p.sizes

        images_by_color = {}
        if isinstance(p.images_by_color, str):
            try:
                images_by_color = json.loads(p.images_by_color)
            except json.JSONDecodeError:
                images_by_color = {}
        elif isinstance(p.images_by_color, dict):
            images_by_color = p.images_by_color

        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "discount_price": p.discount_price,
            "images": images,
            "colors": colors,
            "sizes": sizes,
            "in_stock": p.in_stock,
            "rating": p.rating,
            "reviews": p.reviews,
            "featured": p.featured,
            "best_seller": p.best_seller,
            "new_arrival": p.new_arrival,
            "category_id": p.category_id,
            "subcategory_id": p.subcategory_id,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S") if p.created_at else None,
            "images_by_color": images_by_color,
        })
    return result


# Get Product
@router.get("/get/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Safely convert JSON string fields to list/dict
    if isinstance(product.images, str):
        try:
            product.images = json.loads(product.images)
        except json.JSONDecodeError:
            product.images = []
    elif not product.images:
        product.images = []

    if isinstance(product.colors, str):
        try:
            product.colors = json.loads(product.colors)
        except json.JSONDecodeError:
            product.colors = []
    elif not product.colors:
        product.colors = []

    if isinstance(product.sizes, str):
        try:
            product.sizes = json.loads(product.sizes)
        except json.JSONDecodeError:
            product.sizes = []
    elif not product.sizes:
        product.sizes = []

    if isinstance(product.images_by_color, str):
        try:
            product.images_by_color = json.loads(product.images_by_color)
        except json.JSONDecodeError:
            product.images_by_color = {}
    elif not product.images_by_color:
        product.images_by_color = {}

    return product


# Update Product
@router.put("/update/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    discount_price: float = Form(0),
    category_name: str = Form(None),
    subcategory_name: str = Form(None),
    colors: str = Form(None),
    sizes: str = Form(None),
    in_stock: bool = Form(None),
    rating: float = Form(None),
    reviews: int = Form(None),
    featured: bool = Form(None),
    best_seller: bool = Form(None),
    new_arrival: bool = Form(None),
    images: List[UploadFile] = File(None),
    images_by_color: str = Form(None),  # ✅ NEW FIELD
    db: Session = Depends(get_db)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if name:
        db_product.name = name
    if description:
        db_product.description = description
    if price:
        db_product.price = price
    if discount_price is not None:
        db_product.discount_price = discount_price
    if category_name:
        db_product.category_name = category_name
    if subcategory_name:
        db_product.subcategory_name = subcategory_name
    if colors:
        try:
            color_list = json.loads(colors) if isinstance(colors, str) else []
        except json.JSONDecodeError:
            color_list = [c.strip() for c in colors.split(",")]
        db_product.colors = json.dumps(color_list)
    if sizes:
        try:
            size_list = json.loads(sizes) if isinstance(sizes, str) else []
        except json.JSONDecodeError:
            size_list = [s.strip() for s in sizes.split(",")]
        db_product.sizes = json.dumps(size_list)
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
    if images:
        upload_folder = "static/products"
        os.makedirs(upload_folder, exist_ok=True)

        image_paths = []
        for image in images:
            filename = f"{time.time()}_{image.filename}"
            file_path = os.path.join(upload_folder, filename)
            with open(file_path, "wb") as f:
                f.write(await image.read())
            image_paths.append(f"/static/products/{filename}")
        db_product.images = json.dumps(image_paths)

    if images_by_color:
        try:
            parsed = json.loads(images_by_color)  # ensure valid JSON
            db_product.images_by_color = json.dumps(parsed)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid images_by_color format")

    db.commit()
    db.refresh(db_product)

    # Safely deserialize JSON fields for response
    if isinstance(db_product.images, str):
        try:
            db_product.images = json.loads(db_product.images)
        except json.JSONDecodeError:
            db_product.images = []
    elif not db_product.images:
        db_product.images = []

    if isinstance(db_product.colors, str):
        try:
            db_product.colors = json.loads(db_product.colors)
        except json.JSONDecodeError:
            db_product.colors = []
    elif not db_product.colors:
        db_product.colors = []

    if isinstance(db_product.sizes, str):
        try:
            db_product.sizes = json.loads(db_product.sizes)
        except json.JSONDecodeError:
            db_product.sizes = []
    elif not db_product.sizes:
        db_product.sizes = []

    if isinstance(db_product.images_by_color, str):
        try:
            db_product.images_by_color = json.loads(db_product.images_by_color)
        except json.JSONDecodeError:
            db_product.images_by_color = {}
    elif not db_product.images_by_color:
        db_product.images_by_color = {}

    return db_product


# Delete Product
@router.delete("/delete/{product_id}", response_model=ProductOut)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()

    return db_product
