from sqlalchemy.orm import Session
from app.db.models import Sale, SaleItem, Payment, Customer, Saree, Inventory
from app.schemas.sale import SaleCreate, SalePaymentCreate
from app.services.inventory_service import decrease_stock
from datetime import datetime
from typing import Optional, List
import uuid


def generate_sale_number() -> str:
    return f"SALE-{uuid.uuid4().hex[:6].upper()}"


def generate_payment_number() -> str:
    return f"PAY-{uuid.uuid4().hex[:8].upper()}"


def create_sale(
    db: Session,
    sale_data: SaleCreate,
    created_by: Optional[int] = None
) -> Sale:
    # Validate items and check stock
    items_data = []
    subtotal = 0
    
    for item in sale_data.items:
        saree = db.query(Saree).filter(Saree.id == item.saree_id).first()
        if not saree:
            raise ValueError(f"Saree with ID {item.saree_id} not found")
        if not saree.is_active:
            raise ValueError(f"Saree {saree.name} is not active")
        
        inventory = db.query(Inventory).filter(Inventory.saree_id == item.saree_id).first()
        if not inventory or inventory.quantity < item.quantity:
            raise ValueError(f"Insufficient stock for {saree.name}. Available: {inventory.quantity if inventory else 0}")
        
        item_total = (item.unit_price * item.quantity) - item.discount_amount + item.tax_amount
        subtotal += item_total
        items_data.append({
            "saree_id": item.saree_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "discount_amount": item.discount_amount or 0,
            "tax_amount": item.tax_amount or 0,
            "total_amount": item_total
        })
    
    total_amount = subtotal - (sale_data.discount_amount or 0) + (sale_data.tax_amount or 0)
    
    # Create sale
    sale = Sale(
        sale_number=generate_sale_number(),
        customer_id=sale_data.customer_id,
        subtotal=subtotal,
        discount_amount=sale_data.discount_amount or 0,
        tax_amount=sale_data.tax_amount or 0,
        total_amount=total_amount,
        paid_amount=0,
        notes=sale_data.notes,
        created_by=created_by
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    
    # Create sale items
    for item_data in items_data:
        sale_item = SaleItem(
            sale_id=sale.id,
            **item_data
        )
        db.add(sale_item)
    
    db.commit()
    
    # Decrease stock for each item
    for item in sale_data.items:
        decrease_stock(
            db=db,
            saree_id=item.saree_id,
            quantity=item.quantity,
            reference_type="SALE",
            reference_id=sale.id,
            performed_by=created_by,
            reason=f"Sale {sale.sale_number}"
        )
    
    db.refresh(sale)
    return sale


def process_payment(
    db: Session,
    sale_id: int,
    payment_data: SalePaymentCreate,
    processed_by: Optional[int] = None
) -> Payment:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise ValueError(f"Sale {sale_id} not found")
    
    remaining_amount = sale.total_amount - sale.paid_amount
    if payment_data.amount > remaining_amount:
        raise ValueError(f"Payment amount exceeds remaining balance. Remaining: {remaining_amount}")
    
    payment = Payment(
        payment_number=generate_payment_number(),
        sale_id=sale_id,
        amount=payment_data.amount,
        method=payment_data.method,
        status="PAID",
        reference_id=payment_data.reference_id,
        processed_by=processed_by,
        processed_at=datetime.utcnow()
    )
    db.add(payment)
    
    # Update sale paid amount and status
    sale.paid_amount += payment_data.amount
    if sale.paid_amount >= sale.total_amount:
        sale.payment_status = "PAID"
    else:
        sale.payment_status = "PARTIALLY_PAID"
    
    db.commit()
    db.refresh(payment)
    return payment


def get_sale_by_id(db: Session, sale_id: int) -> Optional[Sale]:
    return db.query(Sale).filter(Sale.id == sale_id).first()


def get_sale_by_number(db: Session, sale_number: str) -> Optional[Sale]:
    return db.query(Sale).filter(Sale.sale_number == sale_number).first()


def get_sales_list(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    customer_id: Optional[int] = None,
    payment_status: Optional[str] = None
) -> tuple[List[Sale], int]:
    query = db.query(Sale)
    
    if customer_id:
        query = query.filter(Sale.customer_id == customer_id)
    if payment_status:
        query = query.filter(Sale.payment_status == payment_status)
    
    total = query.count()
    sales = query.order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()
    
    return sales, total
