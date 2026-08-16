from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InventoryBase(BaseModel):
    saree_id: int


class InventoryAdjustment(BaseModel):
    quantity_change: int = Field(..., description="Positive for add, negative for remove")
    reason: str = Field(..., min_length=1, max_length=500)


class InventoryResponse(BaseModel):
    id: int
    saree_id: int
    quantity: int
    reserved_quantity: int
    last_counted_at: Optional[datetime]
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StockTransactionResponse(BaseModel):
    id: int
    saree_id: int
    transaction_type: str
    quantity_change: int
    quantity_before: int
    quantity_after: int
    reference_type: Optional[str]
    reference_id: Optional[int]
    reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
