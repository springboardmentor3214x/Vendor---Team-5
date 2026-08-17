from pydantic import BaseModel, ConfigDict, Field
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


class VendorDocumentUpdate(BaseModel):
    """Metadata that can be safely changed without replacing the stored file."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    document_type: Optional[str] = Field(default=None, alias="documentType")


class VendorDocumentOut(VendorDocumentBase):
    id: int
    uploaded_by: Optional[int] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True
