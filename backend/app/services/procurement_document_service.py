"""Procurement-request and invoice document lifecycle operations."""

from datetime import datetime
from typing import Any

from app.models.invoice import Invoice
from app.models.invoice_document import InvoiceDocument
from app.models.procurement_request_document import ProcurementRequestDocument


def _list_current(db: Any, model: Any, parent_field: Any, parent_id: int, include_replaced: bool) -> list[Any]:
    documents = db.query(model).filter(parent_field == parent_id).all()
    return documents if include_replaced else [document for document in documents if document.is_current]


def get_procurement_request_document(db: Any, document_id: int) -> ProcurementRequestDocument | None:
    return db.query(ProcurementRequestDocument).filter(ProcurementRequestDocument.id == document_id).first()


def list_procurement_request_documents(db: Any, request_id: int, *, include_replaced: bool = False) -> list[ProcurementRequestDocument]:
    return _list_current(db, ProcurementRequestDocument, ProcurementRequestDocument.request_id, request_id, include_replaced)


def create_procurement_request_document(db: Any, **metadata: Any) -> ProcurementRequestDocument:
    document = ProcurementRequestDocument(**metadata)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def replace_procurement_request_document(db: Any, document_id: int, *, file_name: str, file_path: str,
                                         uploaded_by: int | None = None, file_size: int | None = None,
                                         content_type: str | None = None, document_type: str | None = None) -> ProcurementRequestDocument | None:
    previous = get_procurement_request_document(db, document_id)
    if previous is None:
        return None
    if not previous.is_current:
        raise ValueError("Only the current document version can be replaced")
    previous.is_current, previous.replaced_at, previous.replaced_by = False, datetime.utcnow(), uploaded_by
    replacement = ProcurementRequestDocument(request_id=previous.request_id, document_type=document_type or previous.document_type,
        file_name=file_name, file_path=file_path, file_size=file_size, content_type=content_type, uploaded_by=uploaded_by,
        version=(previous.version or 1) + 1, is_current=True, replaced_document_id=previous.id)
    db.add(replacement)
    db.commit()
    db.refresh(replacement)
    return replacement


def get_invoice_document(db: Any, document_id: int) -> InvoiceDocument | None:
    return db.query(InvoiceDocument).filter(InvoiceDocument.id == document_id).first()


def list_invoice_documents(db: Any, invoice_id: int, *, include_replaced: bool = False) -> list[InvoiceDocument]:
    return _list_current(db, InvoiceDocument, InvoiceDocument.invoice_id, invoice_id, include_replaced)


def create_invoice_document(db: Any, **metadata: Any) -> InvoiceDocument:
    document = InvoiceDocument(**metadata)
    db.add(document)
    _set_legacy_invoice_document_path(db, document.invoice_id, document.file_path)
    db.commit()
    db.refresh(document)
    return document


def replace_invoice_document(db: Any, document_id: int, *, file_name: str, file_path: str,
                             uploaded_by: int | None = None, file_size: int | None = None,
                             content_type: str | None = None, document_type: str | None = None) -> InvoiceDocument | None:
    previous = get_invoice_document(db, document_id)
    if previous is None:
        return None
    if not previous.is_current:
        raise ValueError("Only the current document version can be replaced")
    previous.is_current, previous.replaced_at, previous.replaced_by = False, datetime.utcnow(), uploaded_by
    replacement = InvoiceDocument(invoice_id=previous.invoice_id, document_type=document_type or previous.document_type,
        file_name=file_name, file_path=file_path, file_size=file_size, content_type=content_type, uploaded_by=uploaded_by,
        version=(previous.version or 1) + 1, is_current=True, replaced_document_id=previous.id)
    db.add(replacement)
    _set_legacy_invoice_document_path(db, replacement.invoice_id, replacement.file_path)
    db.commit()
    db.refresh(replacement)
    return replacement


def _set_legacy_invoice_document_path(db: Any, invoice_id: int, file_path: str) -> None:
    """Keep the existing Invoice.supporting_document_url consumer-compatible."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice is not None:
        invoice.supporting_document_url = file_path
