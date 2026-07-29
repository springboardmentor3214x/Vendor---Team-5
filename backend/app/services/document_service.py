"""Vendor document metadata helpers; file storage is intentionally out of scope."""

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
