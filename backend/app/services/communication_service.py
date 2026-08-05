"""Communication helpers compatible with both current and Swathi DB schemas."""

from __future__ import annotations

from datetime import datetime
from pathlib import PurePath
from typing import Any

from app.models.communication import Communication
from app.services.notification_service import create_notification

try:
    from app.models.discussion import Discussion
    from app.models.discussion_participant import DiscussionParticipant
    from app.models.communication_file import CommunicationFile
except ImportError:  # Models arrive with the Swathi DB change.
    Discussion = DiscussionParticipant = CommunicationFile = None


FULL_ACCESS_ROLES = {"Administrator", "Procurement Manager"}
WORKFLOW_ACCESS_ROLES = {"Finance Officer", "Supply Chain Manager"}
READ_ONLY_ROLES = {"Auditor"}
COMMUNICATION_FIELDS = {"sender_id", "receiver_id", "vendor_id", "procurement_request_id", "purchase_order_id",
                        "contract_id", "invoice_id", "discussion_id", "subject", "message", "message_type",
                        "is_read", "read_at", "created_at"}


def _value(item: Any, name: str, default: Any = None) -> Any:
    return item.get(name, default) if isinstance(item, dict) else getattr(item, name, default)


def _columns(model: Any) -> set[str]:
    try:
        return set(model.__table__.columns.keys())
    except (AttributeError, TypeError):
        return set()


def _available(model: Any, required: set[str] = set()) -> bool:
    return model is not None and required <= _columns(model)


def _missing(feature: str) -> dict[str, str]:
    return {"status": "unavailable", "message": f"{feature} requires Swathi DB/migration support."}


def _rows(db: Any, model: Any, filters: dict[str, Any] | None = None, descending: bool = True) -> list[Any]:
    if db is None or model is None:
        return []
    try:
        query, columns = db.query(model), _columns(model)
        for name, value in (filters or {}).items():
            if value is not None and name in columns:
                query = query.filter(getattr(model, name) == value)
        if "created_at" in columns:
            query = query.order_by(getattr(model, "created_at").desc() if descending else getattr(model, "created_at").asc())
        return list(query.all() or [])
    except Exception:
        return []


def send_message(db: Any, sender_id: int, receiver_id: int | None = None, content: str | None = None, *,
                 message: str | None = None, subject: str | None = None, vendor_id: int | None = None,
                 procurement_request_id: int | None = None, message_type: str | None = None, **links: Any) -> Any:
    """Persist a message, using every supported Swathi communication link."""
    body = content if content is not None else message
    if not body or not body.strip():
        raise ValueError("content is required.")
    columns = _columns(Communication)
    requested = {"receiver_id": receiver_id, "vendor_id": vendor_id, "procurement_request_id": procurement_request_id,
                 "purchase_order_id": links.get("purchase_order_id"), "contract_id": links.get("contract_id"),
                 "invoice_id": links.get("invoice_id"), "discussion_id": links.get("discussion_id"),
                 "message_type": message_type}
    unsupported = [key for key in requested if key not in columns]
    if unsupported:
        return _missing(f"Communication fields: {', '.join(unsupported)}")
    if db is None:
        return _missing("A database session is required to send a message.")
    values = {"sender_id": sender_id, "message": body.strip(), "subject": subject, "created_at": datetime.utcnow(),
              **requested, "is_read": False, "read_at": None}
    row = Communication(**{name: value for name, value in values.items() if name in columns and value is not None})
    try:
        db.add(row); db.commit(); db.refresh(row)
    except Exception:
        if db is not None and hasattr(db, "rollback"):
            db.rollback()
        raise
    if receiver_id and receiver_id != sender_id:
        create_message_notification(db, receiver_id, row)
    return row


def list_messages(db: Any, filters: dict[str, Any] | None = None, **kwargs: Any) -> list[Any]:
    """List messages by any migrated Module 7 communication field."""
    return _rows(db, Communication, {**(filters or {}), **kwargs})


def fetch_messages(db: Any, **filters: Any) -> list[Any]:
    """Swathi-compatible name; ``user_id`` matches sender or receiver."""
    user_id = filters.pop("user_id", None)
    rows = _rows(db, Communication, filters, descending=False)
    return [row for row in rows if user_id is None or user_id in {_value(row, "sender_id"), _value(row, "receiver_id")}]


def get_conversation(db: Any, current_user_id: int, other_user_id: int) -> list[Any]:
    if not _available(Communication, {"receiver_id"}):
        return []
    return [row for row in _rows(db, Communication, descending=False)
            if {_value(row, "sender_id"), _value(row, "receiver_id")} == {current_user_id, other_user_id}]


def mark_message_read(db: Any, message_id: int, current_user_id: int) -> Any:
    """Mark a recipient's message read; returns unavailable/None instead of raising."""
    if not _available(Communication, {"receiver_id", "is_read", "read_at"}):
        return _missing("Message read state")
    try:
        row = db.query(Communication).filter(Communication.id == message_id).filter(Communication.receiver_id == current_user_id).first()
        if row is None:
            return None
        row.is_read, row.read_at = True, datetime.utcnow()
        db.commit(); db.refresh(row)
        return row
    except Exception:
        if db is not None and hasattr(db, "rollback"):
            db.rollback()
        return None


def mark_message_as_read(db: Any, message_id: int, user_id: int) -> Any:
    return mark_message_read(db, message_id, user_id)


def create_discussion(db: Any, created_by: int, title: str, participants: list[int], **links: Any) -> Any:
    if db is None or not _available(Discussion, {"title", "created_by_id"}) or not _available(DiscussionParticipant, {"discussion_id", "user_id"}):
        return _missing("Procurement discussions and participant persistence")
    if not title or not title.strip():
        raise ValueError("title is required.")
    columns = _columns(Discussion)
    values = {"title": title.strip(), "created_by_id": created_by, "status": links.pop("status", "OPEN"), **links}
    try:
        discussion = Discussion(**{key: value for key, value in values.items() if key in columns and value is not None})
        db.add(discussion); db.commit(); db.refresh(discussion)
        for user_id in dict.fromkeys([created_by, *participants]):
            db.add(DiscussionParticipant(discussion_id=discussion.id, user_id=user_id))
        db.commit(); db.refresh(discussion)
        create_discussion_notification(db, [user_id for user_id in participants if user_id != created_by], discussion)
        return discussion
    except Exception:
        if db is not None and hasattr(db, "rollback"):
            db.rollback()
        raise


def list_discussions(db: Any, filters: dict[str, Any] | None = None, **kwargs: Any) -> list[Any]:
    return _rows(db, Discussion, {**(filters or {}), **kwargs})


def get_discussion_history(db: Any, filters: dict[str, Any] | None = None) -> list[Any]:
    return list_messages(db, filters or {})


def get_vendor_communication_history(db: Any, vendor_id: int) -> list[Any]: return list_messages(db, {"vendor_id": vendor_id})
def get_procurement_request_communication_history(db: Any, request_id: int) -> list[Any]: return list_messages(db, {"procurement_request_id": request_id})
def get_purchase_order_communication_history(db: Any, po_id: int) -> list[Any]: return list_messages(db, {"purchase_order_id": po_id})
def get_contract_communication_history(db: Any, contract_id: int) -> Any:
    return list_messages(db, {"contract_id": contract_id}) if _available(Communication, {"contract_id"}) else _missing("Contract-linked communication history")
def get_invoice_communication_history(db: Any, invoice_id: int) -> Any:
    return list_messages(db, {"invoice_id": invoice_id}) if _available(Communication, {"invoice_id"}) else _missing("Invoice-linked communication history")


def validate_safe_file_name(file_name: str) -> str:
    if not file_name or PurePath(file_name).name != file_name or file_name in {".", ".."}:
        raise ValueError("file_name must be a plain file name without path components.")
    return file_name


def save_communication_file(db: Any, file_name: str, **metadata: Any) -> Any:
    validate_safe_file_name(file_name)
    if db is None or not _available(CommunicationFile, {"filename", "file_path", "uploaded_by_id"}): return _missing("Communication file persistence")
    values = {"filename": file_name, **metadata}
    if not values.get("file_path") or not values.get("uploaded_by_id"): raise ValueError("file_path and uploaded_by_id are required.")
    row = CommunicationFile(**{key: value for key, value in values.items() if key in _columns(CommunicationFile) and value is not None})
    try: db.add(row); db.commit(); db.refresh(row); return row
    except Exception: db.rollback(); raise


def list_communication_files(db: Any, **filters: Any) -> list[Any]: return _rows(db, CommunicationFile, filters)
def get_communication_file(db: Any, file_id: int, current_user: Any = None) -> Any:
    del current_user
    return next((row for row in _rows(db, CommunicationFile) if _value(row, "id") == file_id), None) if CommunicationFile else _missing("Communication file persistence")


def create_message_notification(db: Any, receiver_id: int, message: Any) -> Any:
    return create_notification(db, receiver_id, "New message", _value(message, "message", str(message)), notification_type="communication", related_entity_id=_value(message, "id"))
def create_discussion_notification(db: Any, participant_ids: list[int], discussion: Any) -> list[Any]:
    return [create_notification(db, user_id, "Discussion update", f"Discussion: {_value(discussion, 'title', 'Discussion')}", notification_type="discussion", related_entity_id=_value(discussion, "id")) for user_id in dict.fromkeys(participant_ids)]


def can_access_communication(current_user: Any, communication: Any, db: Any = None) -> bool:
    del db
    role, user_id = _value(current_user, "role") if not isinstance(current_user, str) else current_user, _value(current_user, "id") if not isinstance(current_user, int) else current_user
    if role in FULL_ACCESS_ROLES or role in READ_ONLY_ROLES: return True
    if user_id is None: return False
    if user_id in {_value(communication, "sender_id"), _value(communication, "receiver_id")} or user_id in (_value(communication, "participant_ids", []) or []): return True
    if role in WORKFLOW_ACCESS_ROLES and any(_value(communication, key) is not None for key in COMMUNICATION_FIELDS - {"sender_id", "receiver_id", "subject", "message", "message_type", "is_read", "read_at", "created_at"}): return True
    return _value(current_user, "vendor_id") is not None and _value(current_user, "vendor_id") == _value(communication, "vendor_id")
