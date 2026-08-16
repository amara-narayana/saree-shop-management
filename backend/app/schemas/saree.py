from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SareeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    brand_id: int
    category_id: int
    fabric_id: int
    color_id: int
    design_id: Optional[int] = None
    collection: Optional[str] = None
    purchase_price: float = Field(..., gt=0)
    selling_price: float = Field(..., gt=0)
    discount_percent: Optional[float] = Field(default=0, ge=0, le=100)
    tax_percent: Optional[float] = Field(default=0, ge=0, le=100)
    supplier_id: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    reorder_level: int = Field(default=5, ge=0)


class SareeCreate(SareeBase):
    sku: Optional[str] = None
    barcode: Optional[str] = None


class SareeUpdate(BaseModel):
    name: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
    fabric_id: Optional[int] = None
    color_id: Optional[int] = None
    design_id: Optional[int] = None
    collection: Optional[str] = None
    purchase_price: Optional[float] = None
    selling_price: Optional[float] = None
    discount_percent: Optional[float] = None
    tax_percent: Optional[float] = None
    supplier_id: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    reorder_level: Optional[int] = None
    is_active: Optional[bool] = None


class SareeResponse(SareeBase):
    id: int
    sku: str
    barcode: Optional[str]
    stock_quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SareeListResponse(BaseModel):
    items: list[SareeResponse]
    total: int
    page: int
    page_size: int
