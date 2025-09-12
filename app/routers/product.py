from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union
import json, os, time

from app.database import get_db
from app.models import User
from app.models.product import Product
from app.schemas.product import ProductOut
from app.authentication import get_current_admin_user

router = APIRouter()

# ---------------------------- HELPERS ----------------------------
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

def parse_product_for_response(product: Product):
    product.colors = safe_parse_list_field(product.colors)
    product.sizes = safe_parse_list_field(product.sizes)
    product.images = safe_parse_list_field(product.images)
    product.highlights = safe_parse_list_field(product.highlights)
    try:
        product.specifications = json.loads(product.specifications) if product.specifications else {}
    except:
        product.specifications = {}
    product.details = product.details or ""
    return product

# ---------------------------- PUBLIC ROUTES ----------------------------
@router.get("/list", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return [parse_product_for_response(p) for p in products]

@router.get("/product/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return parse_product_for_response(product)

@router.get("/new-arrivals", response_model=List[ProductOut])
def get_new_arrivals(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.new_arrival == True).all()
    return [parse_product_for_response(p) for p in products]

@router.get("/best-sellers", response_model=List[ProductOut])
def get_best_sellers(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.best_seller == True).all()
    return [parse_product_for_response(p) for p in products]

# ---------------------------- ADMIN ROUTES ----------------------------
@router.post("/create")
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    discount_price: float = Form(0),
    category_id: int = Form(...),
    subcategory_id: int = Form(...),
    colors: str = Form(...),
    sizes: str = Form(...),
    in_stock: bool = Form(True),
    rating: float = Form(0.0),
    reviews: int = Form(0),
    featured: bool = Form(False),
    best_seller: bool = Form(False),
    new_arrival: bool = Form(False),
    highlights: Union[str, None] = Form(None),
    specifications: Union[str, None] = Form(None),
    details: Union[str, None] = Form(None),
    images: List[UploadFile] = File([]),
    current_user: User = Depends(get_current_admin_user),  # 🔒 ADMIN ONLY
    db: Session = Depends(get_db)
):
    upload_folder = "static/products"
    os.makedirs(upload_folder, exist_ok=True)
    image_paths = []
    for image in images:
        filename = f"{int(time.time()*1000)}_{image.filename}"
        file_path = os.path.join(upload_folder, filename)
        with open(file_path, "wb") as f:
            f.write(await image.read())
        image_paths.append(f"products/{filename}")

    color_list = safe_parse_list_field(colors)
    size_list = safe_parse_list_field(sizes)
    highlight_list = safe_parse_list_field(highlights)

    try:
        spec_dict = json.loads(specifications) if specifications else {}
        if not isinstance(spec_dict, dict):
            raise ValueError
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON in specifications")

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
        highlights=json.dumps(highlight_list),
        specifications=json.dumps(spec_dict),
        details=details,
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"message": "Product created successfully!", "product_id": new_product.id}

@router.put("/update/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    name: Union[str, None] = Form(None),
    description: Union[str, None] = Form(None),
    price: Union[float, None] = Form(None),
    discount_price: Union[float, None] = Form(None),
    category_id: Union[int, None] = Form(None),
    subcategory_id: Union[int, None] = Form(None),
    colors: Union[str, None] = Form(None),
    sizes: Union[str, None] = Form(None),
    in_stock: Union[bool, None] = Form(None),
    rating: Union[float, None] = Form(None),
    reviews: Union[int, None] = Form(None),
    featured: Union[bool, None] = Form(None),
    best_seller: Union[bool, None] = Form(None),
    new_arrival: Union[bool, None] = Form(None),
    highlights: Union[str, None] = Form(None),
    specifications: Union[str, None] = Form(None),
    details: Union[str, None] = Form(None),
    images: Union[List[UploadFile], None] = File(None),
    current_user: User = Depends(get_current_admin_user),  # 🔒 ADMIN ONLY
    db: Session = Depends(get_db),
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if name is not None: db_product.name = name
    if description is not None: db_product.description = description
    if price is not None: db_product.price = price
    if discount_price is not None: db_product.discount_price = discount_price
    if category_id is not None: db_product.category_id = category_id
    if subcategory_id is not None: db_product.subcategory_id = subcategory_id
    if colors is not None: db_product.colors = json.dumps(safe_parse_list_field(colors))
    if sizes is not None: db_product.sizes = json.dumps(safe_parse_list_field(sizes))
    if in_stock is not None: db_product.in_stock = in_stock
    if rating is not None: db_product.rating = rating
    if reviews is not None: db_product.reviews = reviews
    if featured is not None: db_product.featured = featured
    if best_seller is not None: db_product.best_seller = best_seller
    if new_arrival is not None: db_product.new_arrival = new_arrival
    if highlights is not None: db_product.highlights = json.dumps(safe_parse_list_field(highlights))
    if specifications is not None:
        try:
            db_product.specifications = json.dumps(json.loads(specifications))
        except:
            raise HTTPException(status_code=400, detail="Invalid JSON in specifications")
    if details is not None: db_product.details = details

    if images:
        upload_folder = "static/products"
        os.makedirs(upload_folder, exist_ok=True)
        image_paths = []
        for image in images:
            filename = f"{int(time.time() * 1000)}_{image.filename}"
            file_path = os.path.join(upload_folder, filename)
            with open(file_path, "wb") as f:
                f.write(await image.read())
            image_paths.append(f"products/{filename}")
        db_product.images = json.dumps(image_paths)

    db.commit()
    db.refresh(db_product)
    return parse_product_for_response(db_product)

@router.delete("/delete/{product_id}", response_model=ProductOut)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_admin_user),  # 🔒 ADMIN ONLY
    db: Session = Depends(get_db),
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return parse_product_for_response(db_product)
