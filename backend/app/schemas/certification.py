from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CertificationBase(BaseModel):
    vendor_id: int
    certification_name: str
    certificate_number: str
    issuing_authority: Optional[str] = None
    issue_date: datetime
    expiry_date: datetime
    document_url: Optional[str] = None


class CertificationCreate(CertificationBase):
    pass


class CertificationUpdate(BaseModel):
    certification_name: Optional[str] = None
    certificate_number: Optional[str] = None
    issuing_authority: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    document_url: Optional[str] = None


class CertificationOut(CertificationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
