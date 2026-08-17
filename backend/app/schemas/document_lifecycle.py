"""API contracts for versioned request, invoice, and contract documents."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LifecycleDocumentOut(BaseModel):
    """Common read contract shared by the three versioned document types."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    document_type: str
    file_name: str
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    uploaded_by: Optional[int] = None
    uploaded_at: Optional[datetime] = None
    version: int = 1
    is_current: bool = True
    replaced_document_id: Optional[int] = None
    replaced_at: Optional[datetime] = None
    replaced_by: Optional[int] = None


class VendorIssueCreate(BaseModel):
    """Create an operational vendor issue or complaint."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    category: str = Field(min_length=1, max_length=100)
    severity: str = "Medium"
    description: str = Field(min_length=1, max_length=1000)
    purchase_order_id: Optional[int] = Field(default=None, alias="purchaseOrderId")
    assigned_to: Optional[int] = Field(default=None, alias="assignedTo")


class VendorIssueUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    category: Optional[str] = Field(default=None, min_length=1, max_length=100)
    severity: Optional[str] = None
    description: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    status: Optional[str] = None
    assigned_to: Optional[int] = Field(default=None, alias="assignedTo")
    resolution_notes: Optional[str] = Field(default=None, alias="resolutionNotes")


class VendorIssueResolve(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    resolution_notes: str = Field(alias="resolutionNotes", min_length=1, max_length=1000)


class VendorIssueOut(BaseModel):
    """UI-facing issue record with a stable `category` field."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    vendor_id: int
    purchase_order_id: Optional[int] = None
    category: str
    severity: str
    description: str
    status: str
    reported_by: Optional[int] = None
    reported_date: datetime
    assigned_to: Optional[int] = None
    resolution_notes: Optional[str] = None
    resolved_by: Optional[int] = None
    resolved_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class VendorIssueHistoryOut(BaseModel):
    """Issue history supplied alongside an optional performance-history response."""

    model_config = ConfigDict(populate_by_name=True)

    issue_id: int
    purchase_order_id: Optional[int] = None
    category: str
    severity: str
    status: str
    reported_date: datetime
    resolved_date: Optional[datetime] = None
    resolution_notes: Optional[str] = None
