import json
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductOut


# Create product
def create_product(db: Session, product: ProductOut):
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        discount_price=product.discount_price,
        images=json.dumps(product.images),  # convert list to JSON string
        category_id=product.category_id,
        subcategory_id=product.subcategory_id,
        colors=json.dumps(product.colors),
        sizes=json.dumps(product.sizes),
        in_stock=product.in_stock,
        rating=product.rating,
        reviews=product.reviews,
        featured=product.featured,
        best_seller=product.best_seller,
        new_arrival=product.new_arrival,
        highlights = product.highlights,
        specifications = product.specifications,
        details = product.details
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Deserialize for correct API response
    db_product.images = json.loads(db_product.images) if db_product.images else []
    db_product.colors = json.loads(db_product.colors) if db_product.colors else []
    db_product.sizes = json.loads(db_product.sizes) if db_product.sizes else []

    return db_product

# Get multiple products
def get_products(db: Session, skip: int = 0, limit: int = 100):
    products = db.query(Product).offset(skip).limit(limit).all()

    for product in products:
        product.images = json.loads(product.images) if product.images else []
        product.colors = json.loads(product.colors) if product.colors else []
        product.sizes = json.loads(product.sizes) if product.sizes else []

    return products
