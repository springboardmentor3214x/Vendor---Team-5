from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ContractBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    vendor_id: int = Field(alias="vendorId")
    contract_number: str = Field(alias="contractNumber")
    contract_title: str = Field(alias="contractTitle")
    contract_type: Optional[str] = Field(default=None, alias="contractType")
    procurement_category: Optional[str] = Field(default=None, alias="procurementCategory")
    start_date: datetime = Field(alias="startDate")
    end_date: Optional[datetime] = Field(default=None, alias="endDate")
    contract_value: Optional[float] = Field(default=0.0, alias="contractValue")
    payment_terms: Optional[str] = Field(default=None, alias="paymentTerms")
    sla: Optional[str] = Field(default=None, alias="sla")
    warranty_details: Optional[str] = Field(default=None, alias="warrantyDetails")
    responsible_manager: Optional[str] = Field(default=None, alias="responsibleManager")
    document_url: Optional[str] = Field(default=None, alias="documentUrl")
    status: Optional[str] = "Draft"
    compliance_verified: Optional[bool] = Field(default=False, alias="complianceVerified")


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    contract_title: Optional[str] = Field(default=None, alias="contractTitle")
    contract_type: Optional[str] = Field(default=None, alias="contractType")
    procurement_category: Optional[str] = Field(default=None, alias="procurementCategory")
    start_date: Optional[datetime] = Field(default=None, alias="startDate")
    end_date: Optional[datetime] = Field(default=None, alias="endDate")
    contract_value: Optional[float] = Field(default=None, alias="contractValue")
    payment_terms: Optional[str] = Field(default=None, alias="paymentTerms")
    sla: Optional[str] = Field(default=None, alias="sla")
    warranty_details: Optional[str] = Field(default=None, alias="warrantyDetails")
    responsible_manager: Optional[str] = Field(default=None, alias="responsibleManager")
    document_url: Optional[str] = Field(default=None, alias="documentUrl")
    status: Optional[str] = None
    compliance_verified: Optional[bool] = Field(default=None, alias="complianceVerified")


class ContractResponse(ContractBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class ContractRenewalCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    new_end_date: datetime = Field(alias="newEndDate")
    renewal_value: Optional[float] = Field(default=0.0, alias="renewalValue")
    remarks: Optional[str] = None


class ContractRenewalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    contract_id: int = Field(alias="contractId")
    renewal_date: datetime = Field(alias="renewalDate")
    new_end_date: datetime = Field(alias="newEndDate")
    renewal_value: float = Field(alias="renewalValue")
    remarks: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")
