"""Notification helpers with a safe fallback while no Notification model exists."""

from __future__ import annotations

from datetime import datetime
from typing import Any

try:  # The notification table has not been introduced in this branch yet.
    from app.models.notification import Notification  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - exercised by the public fallback tests
    Notification = None


def _unavailable() -> dict[str, str]:
    """Describe the deliberate model/migration dependency without fabricating data."""
    return {
        "status": "unavailable",
        "message": "Notification persistence is unavailable until a Notification model is added.",
    }


def _column_names() -> set[str]:
    return set(Notification.__table__.columns.keys()) if Notification is not None else set()


def get_user_notifications(db: Any, user_id: int) -> list[Any]:
    """Return only notifications owned by ``user_id`` when persistence is available."""
    if db is None or Notification is None:
        return []
    query = db.query(Notification)
    if "user_id" in _column_names() and hasattr(query, "filter"):
        query = query.filter(Notification.user_id == user_id)
    if "created_at" in _column_names() and hasattr(query, "order_by"):
        query = query.order_by(Notification.created_at.desc())
    if hasattr(query, "all"):
        return query.all()
    return []


def get_unread_notifications(db: Any, user_id: int) -> list[Any]:
    """Return the current user's unread notifications without assuming extra columns."""
    if db is None or Notification is None:
        return []
    query = db.query(Notification)
    columns = _column_names()
    if "user_id" in columns and hasattr(query, "filter"):
        query = query.filter(Notification.user_id == user_id)
    if "is_read" in columns and hasattr(query, "filter"):
        query = query.filter(Notification.is_read.is_(False))
    if "created_at" in columns and hasattr(query, "order_by"):
        query = query.order_by(Notification.created_at.desc())
    if hasattr(query, "all"):
        return query.all()
    return []


def mark_notification_as_read(db: Any, notification_id: int, user_id: int) -> Any | None:
    """Mark an owned notification read; never permit a cross-user update."""
    if db is None or Notification is None:
        return None
    query = db.query(Notification)
    if hasattr(query, "filter"):
        query = query.filter(Notification.id == notification_id)
        if "user_id" in _column_names():
            query = query.filter(Notification.user_id == user_id)
    if hasattr(query, "first"):
        notification = query.first()
    else:
        notification = None
    if notification is None:
        return None
    if "is_read" in _column_names():
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification


def create_notification(
    db: Any,
    user_id: int,
    title: str,
    message: str,
    notification_type: str | None = None,
    related_entity_id: int | None = None,
) -> Any:
    """Persist a notification using only columns declared by the current model."""
    if db is None or Notification is None:
        # TODO: replace with persistence once the Notification model/migration exists.
        return _unavailable()

    columns = _column_names()
    values = {"user_id": user_id, "title": title, "message": message}
    optional_values = {
        "notification_type": notification_type,
        "related_entity_id": related_entity_id,
        "is_read": False,
        "created_at": datetime.utcnow(),
    }
    values.update({key: value for key, value in optional_values.items() if key in columns and value is not None})
    notification = Notification(**{key: value for key, value in values.items() if key in columns})
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def create_contract_expiry_notification(db: Any, user_id: int, contract_id: int, days_until_expiry: int) -> Any:
    return create_notification(
        db, user_id, "Contract expiry reminder",
        f"Contract {contract_id} expires in {days_until_expiry} days.",
        notification_type="contract_expiry", related_entity_id=contract_id,
    )


def create_compliance_notification(db: Any, user_id: int, vendor_id: int, message: str) -> Any:
    return create_notification(
        db, user_id, "Compliance update", message,
        notification_type="compliance", related_entity_id=vendor_id,
    )


def send_email_notification(*args: Any, **kwargs: Any) -> dict[str, str]:
    """Safe integration boundary; this service never sends external email itself."""
    return {"status": "placeholder", "channel": "email", "message": "Email delivery is not configured."}


def send_sms_notification(*args: Any, **kwargs: Any) -> dict[str, str]:
    """Safe integration boundary; this service never sends external SMS itself."""
    return {"status": "placeholder", "channel": "sms", "message": "SMS delivery is not configured."}
