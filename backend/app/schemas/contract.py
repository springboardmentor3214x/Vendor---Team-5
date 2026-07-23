from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ContractBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    vendor_id: int = Field(alias="vendorId")
    contract_title: str = Field(alias="contractTitle")
    contract_type: Optional[str] = Field(default=None, alias="contractType")
    start_date: datetime = Field(alias="startDate")
    end_date: Optional[datetime] = Field(default=None, alias="endDate")
    contract_value: Optional[float] = Field(default=0.0, alias="contractValue")
    status: Optional[str] = "active"
    compliance_verified: Optional[bool] = Field(default=False, alias="complianceVerified")


class ContractCreate(ContractBase):
    pass


class ContractResponse(ContractBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")