"""Contract-document metadata and versioning operations."""

from datetime import datetime
from typing import Any

from app.models.contract_document import ContractDocument


def get_contract_document(db: Any, document_id: int) -> ContractDocument | None:
    return db.query(ContractDocument).filter(ContractDocument.id == document_id).first()


def list_contract_documents(
    db: Any, contract_id: int, *, include_replaced: bool = False
) -> list[ContractDocument]:
    documents = db.query(ContractDocument).filter(
        ContractDocument.contract_id == contract_id
    ).all()
    return documents if include_replaced else [doc for doc in documents if doc.is_current]


def create_contract_document(db: Any, **metadata: Any) -> ContractDocument:
    document = ContractDocument(**metadata)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def replace_contract_document(
    db: Any,
    document_id: int,
    *,
    file_name: str,
    file_path: str,
    uploaded_by: int | None = None,
    file_size: int | None = None,
    content_type: str | None = None,
    document_type: str | None = None,
) -> ContractDocument | None:
    """Version a contract document while preserving the old record for audit."""
    previous = get_contract_document(db, document_id)
    if previous is None:
        return None
    if not previous.is_current:
        raise ValueError("Only the current document version can be replaced")

    previous.is_current = False
    previous.replaced_at = datetime.utcnow()
    previous.replaced_by = uploaded_by
    replacement = ContractDocument(
        contract_id=previous.contract_id,
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
