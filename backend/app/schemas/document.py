from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VendorDocumentBase(BaseModel):
    vendor_id: int
    document_type: str  # GST Certificate, PAN Card, Company Registration Certificate, ISO Certificate, NDA, etc.
    file_name: str
    file_path: str
    content_type: Optional[str] = None


class VendorDocumentCreate(VendorDocumentBase):
    pass


class VendorDocumentOut(VendorDocumentBase):
    id: int
    uploaded_by: Optional[int] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True
