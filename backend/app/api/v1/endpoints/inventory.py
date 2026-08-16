from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.schemas.inventory import InventoryResponse, InventoryAdjustment, StockTransactionResponse
from app.services.inventory_service import (
    get_inventory_by_saree_id, adjust_inventory, get_stock_transactions,
    increase_stock, decrease_stock
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/{saree_id}", response_model=InventoryResponse)
def get_inventory_for_saree(saree_id: int, db: Session = Depends(get_db)):
    inventory = get_inventory_by_saree_id(db, saree_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


@router.post("/{saree_id}/adjust", response_model=InventoryResponse)
def adjust_saree_inventory(
    saree_id: int,
    adjustment: InventoryAdjustment,
    current_user_id: int = 1,  # Placeholder for auth
    db: Session = Depends(get_db)
):
    try:
        inventory = adjust_inventory(
            db=db,
            saree_id=saree_id,
            adjustment=adjustment,
            performed_by=current_user_id,
            reference_type="ADJUSTMENT"
        )
        return inventory
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions", response_model=list[StockTransactionResponse])
def get_all_stock_transactions(
    saree_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_stock_transactions(db, saree_id, skip, limit)


@router.get("/{saree_id}/transactions", response_model=list[StockTransactionResponse])
def get_saree_stock_transactions(
    saree_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_stock_transactions(db, saree_id, skip, limit)
