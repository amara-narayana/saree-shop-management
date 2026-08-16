from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.database import get_db
from app.schemas.saree import SareeCreate, SareeUpdate, SareeResponse, SareeListResponse
from app.services.saree_service import (
    create_saree, get_saree_by_id, update_saree, delete_saree,
    search_sarees, get_low_stock_items
)

router = APIRouter(prefix="/sarees", tags=["Sarees"])


@router.post("/", response_model=SareeResponse, status_code=201)
def create_new_saree(saree_data: SareeCreate, db: Session = Depends(get_db)):
    return create_saree(db, saree_data)


@router.get("/", response_model=SareeListResponse)
def list_sarees(
    search: Optional[str] = None,
    brand_id: Optional[int] = None,
    category_id: Optional[int] = None,
    fabric_id: Optional[int] = None,
    color_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    sarees, total = search_sarees(
        db=db,
        search=search,
        brand_id=brand_id,
        category_id=category_id,
        fabric_id=fabric_id,
        color_id=color_id,
        min_price=min_price,
        max_price=max_price,
        skip=skip,
        limit=page_size
    )
    
    return {
        "items": sarees,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/low-stock", response_model=List[SareeResponse])
def get_low_stock_sarees(threshold: int = 5, db: Session = Depends(get_db)):
    return get_low_stock_items(db, threshold)


@router.get("/{saree_id}", response_model=SareeResponse)
def get_saree(saree_id: int, db: Session = Depends(get_db)):
    saree = get_saree_by_id(db, saree_id)
    if not saree:
        raise HTTPException(status_code=404, detail="Saree not found")
    return saree


@router.put("/{saree_id}", response_model=SareeResponse)
def update_existing_saree(saree_id: int, saree_data: SareeUpdate, db: Session = Depends(get_db)):
    saree = get_saree_by_id(db, saree_id)
    if not saree:
        raise HTTPException(status_code=404, detail="Saree not found")
    return update_saree(db, saree, saree_data)


@router.delete("/{saree_id}")
def delete_existing_saree(saree_id: int, db: Session = Depends(get_db)):
    saree = get_saree_by_id(db, saree_id)
    if not saree:
        raise HTTPException(status_code=404, detail="Saree not found")
    delete_saree(db, saree)
    return {"message": "Saree deleted successfully"}
