from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class ProcurementRequestCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")
    department: str
    item_description: str = Field(alias="itemDescription")
    quantity: int = 1
    requested_by: Optional[int] = Field(default=None, alias="requestedBy")


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
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")
    procurement_request_id: int = Field(alias="procurementRequestId")
    vendor_id: int = Field(alias="vendorId")
    contract_id: Optional[int] = Field(default=None, alias="contractId")
    quantity: int = 1
    unit_price: float = Field(default=0.0, alias="unitPrice")
    expected_delivery_date: Optional[datetime] = Field(default=None, alias="expectedDeliveryDate")
    payment_terms: Optional[str] = Field(default=None, alias="paymentTerms")


class PurchaseOrderOut(PurchaseOrderCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    po_number: str
    total_cost: float
    actual_delivery_date: Optional[datetime] = None
    po_status: str
    created_at: datetime
    updated_at: datetime