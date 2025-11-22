from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.inventory import Product

router = APIRouter(prefix="/products", tags=["products"])


class ProductBase(BaseModel):
    name: str
    sku: str
    category: str | None = None
    uom: str
    description: str | None = None
    reorder_level: float = 0
    reorder_qty: float = 0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    uom: str | None = None
    description: str | None = None
    reorder_level: float | None = None
    reorder_qty: float | None = None
    is_active: bool | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    sku: str
    category: str | None
    uom: str
    description: str | None
    reorder_level: float
    reorder_qty: float
    is_active: bool

    class Config:
        orm_mode = True



def get_product_or_404(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product



@router.get("/", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
   
    products = db.query(Product).all()
    return products


@router.post("/", response_model=ProductOut, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product. SKU must be unique.
    """
    existing = db.query(Product).filter(Product.sku == payload.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")

    product = Product(
        name=payload.name,
        sku=payload.sku,
        category=payload.category,
        uom=payload.uom,
        description=payload.description,
        reorder_level=payload.reorder_level,
        reorder_qty=payload.reorder_qty,
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a single product by ID.
    """
    product = get_product_or_404(db, product_id)
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a product (full/partial).
    SKU is not updatable here to avoid complexity.
    """
    product = get_product_or_404(db, product_id)

    # Apply only fields that were provided
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a product by setting is_active = False.
    If you prefer hard delete, you can db.delete(product) instead.
    """
    product = get_product_or_404(db, product_id)

    # Soft delete
    product.is_active = False
    db.add(product)
    db.commit()
    return
