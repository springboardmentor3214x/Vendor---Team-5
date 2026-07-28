from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContractBase(BaseModel):
    vendor_id: int
    contract_number: str
    contract_title: str
    contract_type: Optional[str] = None
    procurement_category: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    contract_value: Optional[float] = 0.0
    payment_terms: Optional[str] = None
    sla: Optional[str] = None
    warranty_details: Optional[str] = None
    responsible_manager: Optional[str] = None
    document_url: Optional[str] = None
    status: Optional[str] = "Draft"
    compliance_verified: Optional[bool] = False


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    contract_title: Optional[str] = None
    contract_type: Optional[str] = None
    procurement_category: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    contract_value: Optional[float] = None
    payment_terms: Optional[str] = None
    sla: Optional[str] = None
    warranty_details: Optional[str] = None
    responsible_manager: Optional[str] = None
    document_url: Optional[str] = None
    status: Optional[str] = None
    compliance_verified: Optional[bool] = None


class ContractResponse(ContractBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContractRenewalCreate(BaseModel):
    new_end_date: datetime
    renewal_value: Optional[float] = 0.0
    remarks: Optional[str] = None


class ContractRenewalOut(BaseModel):
    id: int
    contract_id: int
    renewal_date: datetime
    new_end_date: datetime
    renewal_value: float
    remarks: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True