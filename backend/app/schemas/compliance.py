from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ComplianceRecordBase(BaseModel):
    vendor_id: int
    compliance_type: str
    status: Optional[str] = "Pending Verification"
    remarks: Optional[str] = None


class ComplianceRecordCreate(ComplianceRecordBase):
    pass


class ComplianceVerify(BaseModel):
    status: str  # Compliant, Non-Compliant, Expired
    remarks: Optional[str] = None


class ComplianceRecordOut(ComplianceRecordBase):
    id: int
    verification_date: Optional[datetime] = None
    verified_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
