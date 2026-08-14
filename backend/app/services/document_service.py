"""Vendor document metadata and replacement lifecycle helpers.

File bytes are stored by the route/storage adapter.  This service owns the
database lifecycle so a replacement never destroys the previous audit record.
"""

from datetime import datetime
from typing import Any

from app.models.vendor_document import VendorDocument


def get_vendor_documents(db: Any, vendor_id: int) -> list[VendorDocument]:
    return db.query(VendorDocument).filter(VendorDocument.vendor_id == vendor_id).all()


def get_document_by_id(db: Any, document_id: int) -> VendorDocument | None:
    return db.query(VendorDocument).filter(VendorDocument.id == document_id).first()


def update_document_metadata(db: Any, document_id: int, document_type: str) -> VendorDocument | None:
    """Update only the declared document type; leave file metadata/storage untouched."""
    document = get_document_by_id(db, document_id)
    if document is None:
        return None
    document.document_type = document_type
    db.commit()
    db.refresh(document)
    return document


def create_vendor_document(db: Any, **metadata: Any) -> VendorDocument:
    """Persist metadata for a newly uploaded vendor document."""
    document = VendorDocument(**metadata)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def replace_vendor_document(
    db: Any,
    document_id: int,
    *,
    file_name: str,
    file_path: str,
    uploaded_by: int | None = None,
    file_size: int | None = None,
    content_type: str | None = None,
    document_type: str | None = None,
) -> VendorDocument | None:
    """Create a new current version and retain the replaced vendor document."""
    previous = get_document_by_id(db, document_id)
    if previous is None:
        return None
    if not previous.is_current:
        raise ValueError("Only the current document version can be replaced")

    now = datetime.utcnow()
    previous.is_current = False
    previous.replaced_at = now
    previous.replaced_by = uploaded_by
    replacement = VendorDocument(
        vendor_id=previous.vendor_id,
        document_type=document_type or previous.document_type,
        file_name=file_name,
        file_path=file_path,
        file_size=file_size,
        content_type=content_type,
        uploaded_by=uploaded_by,
        version=(previous.version or 1) + 1,
        is_current=True,
        replaced_document_id=previous.id,
    )
    db.add(replacement)
    db.commit()
    db.refresh(replacement)
    return replacement
