from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db.models import Saree, Sale, Inventory, Supplier, Customer
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    
    # Today's sales
    today_sales = db.query(Sale).filter(
        Sale.created_at >= datetime.combine(today, datetime.min.time())
    ).all()
    today_total = sum(s.total_amount for s in today_sales)
    
    # Total inventory count and value
    total_products = db.query(Saree).filter(Saree.is_active == True).count()
    inventory_value = db.query(
        Saree.purchase_price * Saree.stock_quantity
    ).filter(Saree.is_active == True).all()
    total_inventory_value = sum(float(iv[0]) if iv[0] else 0 for iv in inventory_value)
    
    # Low stock count
    low_stock_count = db.query(Saree).filter(
        Saree.stock_quantity <= Saree.reorder_level,
        Saree.is_active == True
    ).count()
    
    # Customer count
    customer_count = db.query(Customer).filter(Customer.is_active == True).count()
    
    # Supplier count
    supplier_count = db.query(Supplier).filter(Supplier.is_active == True).count()
    
    return {
        "today_sales": len(today_sales),
        "today_revenue": float(today_total),
        "total_products": total_products,
        "inventory_value": total_inventory_value,
        "low_stock_count": low_stock_count,
        "customer_count": customer_count,
        "supplier_count": supplier_count
    }


@router.get("/recent-sales")
def get_recent_sales(limit: int = 10, db: Session = Depends(get_db)):
    sales = db.query(Sale).order_by(Sale.created_at.desc()).limit(limit).all()
    return [
        {
            "id": s.id,
            "sale_number": s.sale_number,
            "customer_id": s.customer_id,
            "total_amount": float(s.total_amount),
            "payment_status": s.payment_status.value,
            "created_at": s.created_at.isoformat()
        }
        for s in sales
    ]


@router.get("/low-stock")
def get_low_stock_items(limit: int = 20, db: Session = Depends(get_db)):
    items = db.query(Saree).filter(
        Saree.stock_quantity <= Saree.reorder_level,
        Saree.is_active == True
    ).limit(limit).all()
    
    return [
        {
            "id": s.id,
            "sku": s.sku,
            "name": s.name,
            "stock_quantity": s.stock_quantity,
            "reorder_level": s.reorder_level
        }
        for s in items
    ]
