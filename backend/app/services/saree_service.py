from sqlalchemy.orm import Session
from app.db.models import Saree, Inventory, StockTransaction
from app.schemas.saree import SareeCreate, SareeUpdate
from typing import Optional, List
from datetime import datetime
import uuid


def generate_sku() -> str:
    return f"SAR-{uuid.uuid4().hex[:6].upper()}"


def generate_barcode() -> str:
    return f"BC{uuid.uuid4().hex[:10].upper()}"


def get_saree_by_id(db: Session, saree_id: int) -> Optional[Saree]:
    return db.query(Saree).filter(Saree.id == saree_id).first()


def get_saree_by_sku(db: Session, sku: str) -> Optional[Saree]:
    return db.query(Saree).filter(Saree.sku == sku).first()


def get_saree_by_barcode(db: Session, barcode: str) -> Optional[Saree]:
    return db.query(Saree).filter(Saree.barcode == barcode).first()


def create_saree(db: Session, saree_data: SareeCreate) -> Saree:
    if not saree_data.sku:
        saree_data.sku = generate_sku()
    if not saree_data.barcode:
        saree_data.barcode = generate_barcode()
    
    saree = Saree(**saree_data.model_dump())
    db.add(saree)
    db.commit()
    db.refresh(saree)
    
    # Create inventory record
    inventory = Inventory(saree_id=saree.id, quantity=0)
    db.add(inventory)
    db.commit()
    
    return saree


def update_saree(db: Session, saree: Saree, update_data: SareeUpdate) -> Saree:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(saree, field, value)
    db.commit()
    db.refresh(saree)
    return saree


def delete_saree(db: Session, saree: Saree) -> bool:
    saree.is_active = False
    db.commit()
    return True


def search_sarees(
    db: Session,
    search: Optional[str] = None,
    brand_id: Optional[int] = None,
    category_id: Optional[int] = None,
    fabric_id: Optional[int] = None,
    color_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 50
) -> tuple[List[Saree], int]:
    query = db.query(Saree).filter(Saree.is_active == True)
    
    if search:
        query = query.filter(
            (Saree.name.ilike(f"%{search}%")) |
            (Saree.sku.ilike(f"%{search}%")) |
            (Saree.barcode.ilike(f"%{search}%"))
        )
    
    if brand_id:
        query = query.filter(Saree.brand_id == brand_id)
    if category_id:
        query = query.filter(Saree.category_id == category_id)
    if fabric_id:
        query = query.filter(Saree.fabric_id == fabric_id)
    if color_id:
        query = query.filter(Saree.color_id == color_id)
    if min_price is not None:
        query = query.filter(Saree.selling_price >= min_price)
    if max_price is not None:
        query = query.filter(Saree.selling_price <= max_price)
    
    total = query.count()
    sarees = query.offset(skip).limit(limit).all()
    
    return sarees, total


def get_low_stock_items(db: Session, threshold: int = 5) -> List[Saree]:
    return db.query(Saree).filter(
        Saree.stock_quantity <= threshold,
        Saree.is_active == True
    ).all()
