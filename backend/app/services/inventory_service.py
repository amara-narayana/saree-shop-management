from sqlalchemy.orm import Session
from app.db.models import Inventory, StockTransaction, Saree
from app.schemas.inventory import InventoryAdjustment
from datetime import datetime
from typing import Optional


def get_inventory_by_saree_id(db: Session, saree_id: int) -> Optional[Inventory]:
    return db.query(Inventory).filter(Inventory.saree_id == saree_id).first()


def create_stock_transaction(
    db: Session,
    saree_id: int,
    inventory_id: int,
    transaction_type: str,
    quantity_change: int,
    quantity_before: int,
    quantity_after: int,
    reference_type: Optional[str] = None,
    reference_id: Optional[int] = None,
    reason: Optional[str] = None,
    performed_by: Optional[int] = None
) -> StockTransaction:
    transaction = StockTransaction(
        saree_id=saree_id,
        inventory_id=inventory_id,
        transaction_type=transaction_type,
        quantity_change=quantity_change,
        quantity_before=quantity_before,
        quantity_after=quantity_after,
        reference_type=reference_type,
        reference_id=reference_id,
        reason=reason,
        performed_by=performed_by
    )
    db.add(transaction)
    return transaction


def adjust_inventory(
    db: Session,
    saree_id: int,
    adjustment: InventoryAdjustment,
    performed_by: Optional[int] = None,
    reference_type: Optional[str] = None,
    reference_id: Optional[int] = None
) -> Inventory:
    inventory = get_inventory_by_saree_id(db, saree_id)
    if not inventory:
        raise ValueError(f"Inventory not found for saree {saree_id}")
    
    quantity_before = inventory.quantity
    new_quantity = quantity_before + adjustment.quantity_change
    
    if new_quantity < 0:
        raise ValueError("Cannot have negative inventory")
    
    inventory.quantity = new_quantity
    inventory.updated_at = datetime.utcnow()
    
    # Create stock transaction
    transaction = create_stock_transaction(
        db=db,
        saree_id=saree_id,
        inventory_id=inventory.id,
        transaction_type="ADJUSTMENT",
        quantity_change=adjustment.quantity_change,
        quantity_before=quantity_before,
        quantity_after=new_quantity,
        reference_type=reference_type,
        reference_id=reference_id,
        reason=adjustment.reason,
        performed_by=performed_by
    )
    db.add(transaction)
    db.commit()
    db.refresh(inventory)
    
    # Update saree stock_quantity
    saree = db.query(Saree).filter(Saree.id == saree_id).first()
    if saree:
        saree.stock_quantity = new_quantity
        db.commit()
    
    return inventory


def increase_stock(
    db: Session,
    saree_id: int,
    quantity: int,
    reference_type: str,
    reference_id: int,
    performed_by: Optional[int] = None,
    reason: Optional[str] = None
) -> Inventory:
    """Increase stock (e.g., from purchase receiving)"""
    inventory = get_inventory_by_saree_id(db, saree_id)
    if not inventory:
        raise ValueError(f"Inventory not found for saree {saree_id}")
    
    quantity_before = inventory.quantity
    new_quantity = quantity_before + quantity
    
    inventory.quantity = new_quantity
    inventory.updated_at = datetime.utcnow()
    
    transaction = create_stock_transaction(
        db=db,
        saree_id=saree_id,
        inventory_id=inventory.id,
        transaction_type="PURCHASE",
        quantity_change=quantity,
        quantity_before=quantity_before,
        quantity_after=new_quantity,
        reference_type=reference_type,
        reference_id=reference_id,
        reason=reason,
        performed_by=performed_by
    )
    db.add(transaction)
    db.commit()
    db.refresh(inventory)
    
    # Update saree stock_quantity
    saree = db.query(Saree).filter(Saree.id == saree_id).first()
    if saree:
        saree.stock_quantity = new_quantity
        db.commit()
    
    return inventory


def decrease_stock(
    db: Session,
    saree_id: int,
    quantity: int,
    reference_type: str,
    reference_id: int,
    performed_by: Optional[int] = None,
    reason: Optional[str] = None
) -> Inventory:
    """Decrease stock (e.g., from sale)"""
    inventory = get_inventory_by_saree_id(db, saree_id)
    if not inventory:
        raise ValueError(f"Inventory not found for saree {saree_id}")
    
    if inventory.quantity < quantity:
        raise ValueError(f"Insufficient stock. Available: {inventory.quantity}, Requested: {quantity}")
    
    quantity_before = inventory.quantity
    new_quantity = quantity_before - quantity
    
    inventory.quantity = new_quantity
    inventory.updated_at = datetime.utcnow()
    
    transaction = create_stock_transaction(
        db=db,
        saree_id=saree_id,
        inventory_id=inventory.id,
        transaction_type="SALE",
        quantity_change=-quantity,
        quantity_before=quantity_before,
        quantity_after=new_quantity,
        reference_type=reference_type,
        reference_id=reference_id,
        reason=reason,
        performed_by=performed_by
    )
    db.add(transaction)
    db.commit()
    db.refresh(inventory)
    
    # Update saree stock_quantity
    saree = db.query(Saree).filter(Saree.id == saree_id).first()
    if saree:
        saree.stock_quantity = new_quantity
        db.commit()
    
    return inventory


def get_stock_transactions(
    db: Session,
    saree_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> list:
    query = db.query(StockTransaction)
    if saree_id:
        query = query.filter(StockTransaction.saree_id == saree_id)
    
    return query.order_by(StockTransaction.created_at.desc()).offset(skip).limit(limit).all()
