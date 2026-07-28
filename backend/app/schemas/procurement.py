from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ProcurementRequestCreate(BaseModel):
    department: str
    item_description: str
    quantity: int = 1
    requested_by: Optional[int] = None


class ProcurementRequestOut(ProcurementRequestCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    request_number: str
    request_date: datetime
    approval_status: str
    approved_by: Optional[int] = None
    approved_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class PurchaseOrderCreate(BaseModel):
    procurement_request_id: int
    vendor_id: int
    contract_id: Optional[int] = None
    quantity: int = 1
    unit_price: float = 0.0
    expected_delivery_date: Optional[datetime] = None
    payment_terms: Optional[str] = None


class PurchaseOrderOut(PurchaseOrderCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    po_number: str
    total_cost: float
    actual_delivery_date: Optional[datetime] = None
    po_status: str
    created_at: datetime
    updated_at: datetime