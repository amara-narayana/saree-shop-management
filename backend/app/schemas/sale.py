from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.core.enums import PaymentMethod, PaymentStatus


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SaleItemBase(BaseModel):
    saree_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    discount_amount: Optional[float] = Field(default=0, ge=0)
    tax_amount: Optional[float] = Field(default=0, ge=0)


class SaleItemCreate(SaleItemBase):
    pass


class SaleItemResponse(SaleItemBase):
    id: int
    sale_id: int
    total_amount: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class SaleCreate(BaseModel):
    customer_id: Optional[int] = None
    items: List[SaleItemCreate]
    discount_amount: Optional[float] = Field(default=0, ge=0)
    tax_amount: Optional[float] = Field(default=0, ge=0)
    notes: Optional[str] = None


class SalePaymentCreate(BaseModel):
    amount: float = Field(..., gt=0)
    method: PaymentMethod
    reference_id: Optional[str] = None


class SaleResponse(BaseModel):
    id: int
    sale_number: str
    customer_id: Optional[int]
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    paid_amount: float
    payment_status: PaymentStatus
    sale_status: str
    notes: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    id: int
    payment_number: str
    sale_id: int
    amount: float
    currency: str
    method: PaymentMethod
    status: PaymentStatus
    provider: Optional[str]
    provider_transaction_id: Optional[str]
    reference_id: Optional[str]
    processed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
