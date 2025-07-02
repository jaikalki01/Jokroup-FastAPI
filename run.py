from datetime import datetime
from typing import Optional, List

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager

import os

from app.database import init_db, engine, Base
from app.routers import (
    address,
    coupon as coupon_router,
    category as category_router,
    product as product_router,
    admin as admin_router,
    authentication as auth_router,
    order,
    image_upload,
)
from app.routers.user import router as user_router

# Run database creation
Base.metadata.create_all(bind=engine)

# Lifespan event for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

# Create FastAPI app with metadata
app = FastAPI(
    title="Jokroup API",
    description="API for Templamart where users can buy and sell templates.",
    version="1.0.0",
    lifespan=lifespan,
)

# Mount static files (for serving images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")



# Middleware
SECRET_KEY = os.urandom(24).hex()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(address.router, prefix="/api/v1/address", tags=["Address"])
app.include_router(coupon_router.router, prefix="/api/v1/coupon", tags=["Coupon"])
app.include_router(category_router.router, prefix="/api/v1/cat", tags=["Category & SubCategory"])
app.include_router(product_router.router, prefix="/api/v1/product", tags=["Product"])
app.include_router(admin_router.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(order.router, prefix="/api/orders", tags=["Orders"])









#from datetime import datetime

class Address(BaseModel):
    id: str
    name: str
    line1: str
    line2: Optional[str] = None
    city: str
    state: str
    postalCode: str
    country: str
    phone: str
    default: bool

# Define the User model
class User(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    password: str
    role: str
    avatar: Optional[str] = '/placeholder.svg'
    addresses: List[Address]
    createdAt: datetime

# Product schema
class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float  # Change to float for decimal prices
    images: List[str]
    category: str  # Could be a reference to a Category model if necessary
    subcategory: str  # Could also be a reference to a Subcategory model
    colors: List[str]
    sizes: List[str]
    inStock: bool
    rating: float
    reviews: int
    featured: Optional[bool] = None
    bestSeller: Optional[bool] = None
    newArrival: Optional[bool] = None
    discountPrice: Optional[float] = None  # Change to float for decimals
    createdAt: datetime  # Change to datetime type for date validation

# Subcategory model
class Subcategory(BaseModel):
    id: str
    name: str
    slug: str

# Category model, which includes subcategories
class Category(BaseModel):
    id: str
    name: str
    slug: str
    subcategories: List[Subcategory]  # Use Subcategory model instead of plain dict

# Coupon schema
class Coupon(BaseModel):
    id: str
    code: str
    description: str
    discountType: str
    discountValue: float  # Keep as float for percentage discounts
    minimumPurchase: float
    validFrom: datetime  # Change to datetime for better date validation
    validTo: datetime    # Change to datetime for better date validation
    maxUses: int
    usedCount: int
    active: bool

# Mock product data
products_data = [
  {
    "id": "1",
    "name": "Classic White T-Shirtafrgg",
    "description": "A timeless classic white t-shirt made from 100% organic cotton.",
    "price": 699,
    "images": ["/placeholder.svg", "/placeholder.svg"],
    "category": "men",
    "subcategory": "men-tshirts",
    "colors": ["white", "black", "gray"],
    "sizes": ["S", "M", "L", "XL"],
    "inStock": True,
    "rating": 4.5,
    "reviews": 128,
    "featured": True,
    "bestSeller": True,
    "createdAt": "2023-01-15T10:30:00Z"
  },
  {
    "id": "2",
    "name": "Slim Fit Jeans",
    "description": "Classic slim fit jeans with a modern twist. Perfect for any casual occasion.",
    "price": 1499,
    "images": ["/placeholder.svg", "/placeholder.svg"],
    "category": "men",
    "subcategory": "men-jeans",
    "colors": ["blue", "black", "gray"],
    "sizes": ["30", "32", "34", "36"],
    "inStock": True,
    "rating": 4.2,
    "reviews": 95,
    "createdAt": "2023-02-12T14:45:00Z"
  },
  {
    "id": "3",
    "name": "Floral Summer Dress",
    "description": "Beautiful floral pattern dress perfect for summer days.",
    "price": 1299,
    "discountPrice": 999,
    "images": ["/placeholder.svg", "/placeholder.svg"],
    "category": "women",
    "subcategory": "women-dresses",
    "colors": ["red", "blue", "green"],
    "sizes": ["XS", "S", "M", "L"],
    "inStock": True,
    "rating": 4.8,
    "reviews": 215,
    "featured": True,
    "newArrival": True,
    "createdAt": "2023-03-05T09:15:00Z"
  },
  {
    "id": "4",
    "name": "High-Waist Skinny Jeans",
    "description": "Modern high-waist skinny jeans with stretch comfort.",
    "price": 1899,
    "images": ["/placeholder.svg", "/placeholder.svg"],
    "category": "women",
    "subcategory": "women-jeans",
    "colors": ["blue", "black"],
    "sizes": ["26", "28", "30", "32"],
    "inStock": True,
    "rating": 4.3,
    "reviews": 167,
    "bestSeller": True,
    "createdAt": "2023-04-18T11:30:00Z"
  },
  {
    "id": "5",
    "name": "Kids Dinosaur T-Shirt",
    "description": "Fun dinosaur printed t-shirt for kids who love adventure.",
    "price": 499,
    "images": ["/placeholder.svg", "/placeholder.svg"],
    "category": "kids",
    "subcategory": "kids-boys",
    "colors": ["green", "blue", "orange"],
    "sizes": ["3-4Y", "5-6Y", "7-8Y"],
    "inStock": True,
    "rating": 4.7,
    "reviews": 89,
    "createdAt": "2023-05-10T08:45:00Z"
  },
  {
    "id": "6",
    "name": "Girls Party Dress",
    "description": "Elegant party dress for little princesses.",
    "price": 999,
    "images": ["/placeholder.svg", "/placeholder.svg"],
    "category": "kids",
    "subcategory": "kids-girls",
    "colors": ["pink", "purple", "white"],
    "sizes": ["3-4Y", "5-6Y", "7-8Y"],
    "inStock": True,
    "rating": 4.9,
    "reviews": 76,
    "featured": True,
    "createdAt": "2023-06-01T15:20:00Z"
  },
  {
    "id": "7",
    "name": "Leather Messenger Bag",
    "description": "Stylish leather messenger bag for work and casual use.",
    "price": 2999,
    "discountPrice": 2499,
    "images": ["/placeholder.svg", "/placeholder.svg"],
    "category": "accessories",
    "subcategory": "accessories-bags",
    "colors": ["brown", "black"],
    "sizes": ["ONE SIZE"],
    "inStock": True,
    "rating": 4.6,
    "reviews": 104,
    "createdAt": "2023-07-08T13:10:00Z"
  },
  {
    "id": "8",
    "name": "Classic Analog Watch",
    "description": "Elegant analog watch with leather strap.",
    "price": 1799,
    "images": ["/placeholder.svg", "/placeholder.svg"],
    "category": "accessories",
    "subcategory": "accessories-watches",
    "colors": ["silver", "gold", "rose-gold"],
    "sizes": ["ONE SIZE"],
    "inStock": True,
    "rating": 4.4,
    "reviews": 128,
    "newArrival": True,
    "bestSeller": True,
    "createdAt": "2023-08-15T10:30:00Z"
  },
  {
    "id": "9",
    "name": "Formal Business Shirt",
    "description": "Professional formal shirt for business meetings and office wear.",
    "price": 1299,
    "images": ["/placeholder.svg", "/placeholder.svg"],
    "category": "men",
    "subcategory": "men-shirts",
    "colors": ["white", "blue", "light-blue"],
    "sizes": ["S", "M", "L", "XL", "XXL"],
    "inStock": True,
    "rating": 4.3,
    "reviews": 85,
    "createdAt": "2023-09-20T09:40:00Z"
  },
  {
    "id": "10",
    "name": "Women's Casual Blouse",
    "description": "Lightweight casual blouse perfect for everyday wear.",
    "price": 899,
    "images": ["/placeholder.svg", "/placeholder.svg"],
    "category": "women",
    "subcategory": "women-tops",
    "colors": ["white", "black", "red", "blue"],
    "sizes": ["XS", "S", "M", "L", "XL"],
    "inStock": True,
    "rating": 4.2,
    "reviews": 112,
    "newArrival": True,
    "createdAt": "2023-10-05T14:15:00Z"
  },
  {
    "id": "11",
    "name": "Winter Jacket",
    "description": "Warm winter jacket with faux fur hood.",
    "price": 3499,
    "discountPrice": 2999,
    "images": ["/placeholder.svg", "/placeholder.svg"],
    "category": "men",
    "subcategory": "men-jackets",
    "colors": ["black", "navy", "olive"],
    "sizes": ["S", "M", "L", "XL"],
    "inStock": True,
    "rating": 4.7,
    "reviews": 142,
    "featured": True,
    "createdAt": "2023-11-10T11:25:00Z"
  },
  {
    "id": "12",
    "name": "Midi Skirt",
    "description": "Elegant midi skirt for both casual and formal occasions.",
    "price": 1199,
    "images": ["/placeholder.svg", "/placeholder.svg"],
    "category": "women",
    "subcategory": "women-skirts",
    "colors": ["black", "navy", "beige"],
    "sizes": ["XS", "S", "M", "L"],
    "inStock": True,
    "rating": 4.4,
    "reviews": 78,
    "bestSeller": True,
    "createdAt": "2023-12-18T13:50:00Z"
  }
]




# Assuming User and Address classes are already defined...

users = [
    User(
        id='1',
        firstName='Admin',
        lastName='User',
        email='admin@jokroup.com',
        password='admin123',
        role='admin',
        avatar='/placeholder.svg',
        addresses=[
            Address(
                id='1',
                name='Home',
                line1='123 Admin Street',
                city='Mumbai',
                state='Maharashtra',
                postalCode='400001',
                country='India',
                phone='9876543210',
                default=True
            )
        ],
        createdAt=datetime.fromisoformat('2023-01-01T00:00:00')
    ),
    User(
        id='2',
        firstName='John',
        lastName='Doe',
        email='john@example.com',
        password='password123',
        role='user',
        addresses=[
            Address(
                id='2',
                name='Home',
                line1='456 Main St',
                city='Delhi',
                state='Delhi',
                postalCode='110001',
                country='India',
                phone='9876543211',
                default=True
            ),
            Address(
                id='3',
                name='Office',
                line1='789 Work Ave',
                line2='Floor 5',
                city='Delhi',
                state='Delhi',
                postalCode='110002',
                country='India',
                phone='9876543212',
                default=False
            )
        ],
        createdAt=datetime.fromisoformat('2023-01-15T10:30:00')
    ),
    User(
        id='3',
        firstName='Jane',
        lastName='Smith',
        email='jane@example.com',
        password='password456',
        role='user',
        avatar='/placeholder.svg',
        addresses=[
            Address(
                id='4',
                name='Home',
                line1='101 Residential Blvd',
                city='Bangalore',
                state='Karnataka',
                postalCode='560001',
                country='India',
                phone='9876543213',
                default=True
            )
        ],
        createdAt=datetime.fromisoformat('2023-02-20T15:45:00')
    )
]




# Mock data for categories
categories_data = [
    Category(
        id="1",
        name="Menaaaaaaaa",
        slug="men",
        subcategories=[
            Subcategory(id="1-1", name="T-Shirts", slug="men-tshirts"),
            Subcategory(id="1-2", name="Shirts", slug="men-shirts"),
            Subcategory(id="1-3", name="Jeans", slug="men-jeans"),
            Subcategory(id="1-4", name="Trousers", slug="men-trousers"),
            Subcategory(id="1-5", name="Jackets", slug="men-jackets"),
        ]
    ),
    Category(
        id="2",
        name="Women",
        slug="women",
        subcategories=[
            Subcategory(id="2-1", name="Dresses", slug="women-dresses"),
            Subcategory(id="2-2", name="Tops", slug="women-tops"),
            Subcategory(id="2-3", name="Jeans", slug="women-jeans"),
            Subcategory(id="2-4", name="Skirts", slug="women-skirts"),
            Subcategory(id="2-5", name="Jackets", slug="women-jackets"),
        ]
    ),
    Category(
        id="3",
        name="Kids",
        slug="kids",
        subcategories=[
            Subcategory(id="3-1", name="Boys", slug="kids-boys"),
            Subcategory(id="3-2", name="Girls", slug="kids-girls"),
        ]
    ),
    Category(
        id="4",
        name="Accessories",
        slug="accessories",
        subcategories=[
            Subcategory(id="4-1", name="Bags", slug="accessories-bags"),
            Subcategory(id="4-2", name="Watches", slug="accessories-watches"),
            Subcategory(id="4-3", name="Jewelry", slug="accessories-jewelry"),
        ]
    ),
]




# Assuming Coupon class and other imports are already defined...

coupons = [
    Coupon(
        id='1',
        code='WELCOME10',
        description='10% off on your first order',
        discountType='percentage',
        discountValue=10,
        minimumPurchase=500,
        validFrom=datetime.fromisoformat('2023-01-01T00:00:00'),
        validTo=datetime.fromisoformat('2025-12-31T23:59:59'),
        maxUses=1000,
        usedCount=450,
        active=True
    ),
    Coupon(
        id='2',
        code='SUMMER2023',
        description='15% off on summer collection',
        discountType='percentage',
        discountValue=15,
        minimumPurchase=1000,
        validFrom=datetime.fromisoformat('2023-03-15T00:00:00'),
        validTo=datetime.fromisoformat('2025-03-15T23:59:59'),
        maxUses=500,
        usedCount=320,
        active=False
    ),
    Coupon(
        id='3',
        code='FLAT200',
        description='Flat ₹200 off on orders above ₹2000',
        discountType='fixed',
        discountValue=200,
        minimumPurchase=2000,
        validFrom=datetime.fromisoformat('2023-03-15T00:00:00'),
        validTo=datetime.fromisoformat('2025-03-15T23:59:59'),
        usedCount=180,
        active=True,
        maxUses=500  # Added maxUses to match the schema
    )
]


# Routes


@app.get("/api/users", response_model=List[User])
async def get_users():
    return users

@app.get("/api/categories", response_model=List[Category])
async def get_categories():
    return categories_data

@app.get("/api/coupons", response_model=List[Coupon])
async def get_coupons():
    return coupons





if __name__ == "__main__":
    uvicorn.run("run:app", host="127.0.0.1", port=8000, reload=True,  log_level="debug")
