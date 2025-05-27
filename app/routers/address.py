from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import address as address_crud
from app.schemas import address as address_schema

router = APIRouter()

@router.post("/", response_model=address_schema.AddressOut)
def create_address(address: address_schema.AddressCreate, db: Session = Depends(get_db)):
    return address_crud.create_address(db, address)

@router.get("/", response_model=list[address_schema.AddressOut])
def read_addresses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return address_crud.get_addresses(db, skip=skip, limit=limit)
