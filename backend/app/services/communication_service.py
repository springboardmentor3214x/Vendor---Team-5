"""Service-layer helpers for the currently migrated communications table.

Direct recipients, read state, discussions, participants and communication files
are intentionally not fabricated here: their columns/tables are not present.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import PurePath
from typing import Any

from app.models.communication import Communication
from app.models.purchase_order import PurchaseOrder
from app.services.notification_service import create_notification


FULL_ACCESS_ROLES = {"Administrator", "Procurement Manager"}
WORKFLOW_ACCESS_ROLES = {"Finance Officer", "Supply Chain Manager"}
READ_ONLY_ROLES = {"Auditor"}


def _value(item: Any, name: str, default: Any = None) -> Any:
    return item.get(name, default) if isinstance(item, dict) else getattr(item, name, default)


def _role(user: Any) -> str | None:
    return _value(user, "role") if not isinstance(user, str) else user


def _user_id(user: Any) -> int | None:
    return _value(user, "id") if not isinstance(user, int) else user


def _rows(db: Any, model: Any, filters: dict[str, Any] | None = None) -> list[Any]:
    if db is None:
        return []
    try:
        query = db.query(model)
        for name, value in (filters or {}).items():
            if value is not None and hasattr(model, name):
                query = query.filter(getattr(model, name) == value)
        return list(query.order_by(model.created_at.desc()).all() or [])
    except Exception:
        return []


def _missing(feature: str) -> dict[str, str]:
    return {"status": "unavailable", "message": f"{feature} requires a Swathi DB/migration change."}


def send_message(
    db: Any,
    sender_id: int,
    receiver_id: int | None = None,
    content: str | None = None,
    *,
    message: str | None = None,
    subject: str | None = None,
    vendor_id: int | None = None,
    procurement_request_id: int | None = None,
    **_links: Any,
) -> Communication | dict[str, str]:
    """Persist a vendor/procurement message supported by the current schema.

    A receiver cannot be safely accepted until ``communications.receiver_id`` is
    migrated; linked vendor/request messages remain fully supported.
    """
    body = content if content is not None else message
    if not body or not body.strip():
        raise ValueError("content is required.")
    if receiver_id is not None:
        return _missing("Vendor-user messaging")
    if db is None:
        raise ValueError("A database session is required to send a message.")
    row = Communication(sender_id=sender_id, message=body.strip(), subject=subject,
                        vendor_id=vendor_id, procurement_request_id=procurement_request_id,
                        created_at=datetime.utcnow())
    try:
        db.add(row)
        db.commit()
        db.refresh(row)
    except Exception:
        db.rollback()
        raise
    return row


def list_messages(db: Any, filters: dict[str, Any] | None = None) -> list[Communication]:
    return _rows(db, Communication, filters)


def get_conversation(db: Any, current_user_id: int, other_user_id: int) -> list[Communication]:
    """Direct conversations are unavailable until recipient persistence exists."""
    del db, current_user_id, other_user_id
    return []


def mark_message_read(db: Any, message_id: int, current_user_id: int) -> dict[str, str]:
    del db, message_id, current_user_id
    return _missing("Message read state")


def create_discussion(db: Any, created_by: int, title: str, participants: list[int], **links: Any) -> dict[str, str]:
    del db, created_by, title, participants, links
    return _missing("Procurement discussions and participant persistence")


def list_discussions(db: Any, filters: dict[str, Any] | None = None) -> list[Any]:
    del db, filters
    return []


def get_discussion_history(db: Any, filters: dict[str, Any] | None = None) -> list[Any]:
    return list_discussions(db, filters)


def get_vendor_communication_history(db: Any, vendor_id: int) -> list[Communication]:
    return list_messages(db, {"vendor_id": vendor_id})


def get_procurement_request_communication_history(db: Any, request_id: int) -> list[Communication]:
    return list_messages(db, {"procurement_request_id": request_id})


def get_purchase_order_communication_history(db: Any, po_id: int) -> list[Communication]:
    """Use the existing PO's request/vendor links; no PO column is required."""
    if db is None:
        return []
    try:
        order = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    except Exception:
        return []
    if order is None:
        return []
    rows = get_procurement_request_communication_history(db, order.procurement_request_id)
    return [row for row in rows if getattr(row, "vendor_id", None) in {None, order.vendor_id}]


def get_contract_communication_history(db: Any, contract_id: int) -> dict[str, str]:
    del db, contract_id
    return _missing("Contract-linked communication history")


def validate_safe_file_name(file_name: str) -> str:
    """Reject path traversal before a future file-storage integration uses a name."""
    if not file_name or PurePath(file_name).name != file_name or file_name in {".", ".."}:
        raise ValueError("file_name must be a plain file name without path components.")
    return file_name


def save_communication_file(db: Any, file_name: str, **metadata: Any) -> dict[str, str]:
    del db, metadata
    validate_safe_file_name(file_name)
    return _missing("Communication file persistence")


def get_communication_file(db: Any, file_id: int, current_user: Any) -> dict[str, str]:
    del db, file_id, current_user
    return _missing("Communication file persistence")


def create_message_notification(db: Any, receiver_id: int, message: Any) -> Any:
    """Delegate to the shared notification service; it reports missing persistence."""
    return create_notification(db, receiver_id, "New message", _value(message, "message", str(message)),
                               notification_type="communication", related_entity_id=_value(message, "id"))


def create_discussion_notification(db: Any, participant_ids: list[int], discussion: Any) -> list[Any]:
    title = _value(discussion, "title", "Discussion")
    return [create_notification(db, user_id, "Discussion update", f"Discussion: {title}",
                                notification_type="discussion", related_entity_id=_value(discussion, "id"))
            for user_id in dict.fromkeys(participant_ids)]


def can_access_communication(current_user: Any, communication: Any, db: Any = None) -> bool:
    """Apply role and ownership checks using only data currently available."""
    del db
    role = _role(current_user)
    if role in FULL_ACCESS_ROLES or role in READ_ONLY_ROLES:
        return True
    user_id = _user_id(current_user)
    if user_id is None:
        return False
    if user_id == _value(communication, "sender_id"):
        return True
    participants = _value(communication, "participant_ids", []) or []
    if user_id in participants:
        return True
    if role in WORKFLOW_ACCESS_ROLES and any(_value(communication, name) is not None for name in
                                             ("vendor_id", "procurement_request_id", "purchase_order_id", "contract_id")):
        return True
    vendor_id = _value(current_user, "vendor_id")
    return vendor_id is not None and vendor_id == _value(communication, "vendor_id")
