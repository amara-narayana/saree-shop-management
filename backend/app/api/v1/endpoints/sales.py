from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.schemas.sale import SaleCreate, SaleResponse, SalePaymentCreate, PaymentResponse
from app.services.sale_service import create_sale, process_payment, get_sale_by_id, get_sales_list

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("/", response_model=SaleResponse, status_code=201)
def create_new_sale(
    sale_data: SaleCreate,
    current_user_id: int = 1,  # Placeholder for auth
    db: Session = Depends(get_db)
):
    try:
        return create_sale(db, sale_data, created_by=current_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[SaleResponse])
def list_sales(
    skip: int = 0,
    limit: int = 50,
    customer_id: Optional[int] = None,
    payment_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    sales, _ = get_sales_list(db, skip, limit, customer_id, payment_status)
    return sales


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = get_sale_by_id(db, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


@router.post("/{sale_id}/payment", response_model=PaymentResponse)
def process_sale_payment(
    sale_id: int,
    payment_data: SalePaymentCreate,
    current_user_id: int = 1,  # Placeholder for auth
    db: Session = Depends(get_db)
):
    try:
        return process_payment(db, sale_id, payment_data, processed_by=current_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
