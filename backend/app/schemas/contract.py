from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContractBase(BaseModel):
    vendor_id: int
    contract_title: str
    contract_type: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    contract_value: Optional[float] = 0.0
    status: Optional[str] = "active"
    compliance_verified: Optional[bool] = False


class ContractCreate(ContractBase):
    pass


class ContractResponse(ContractBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True