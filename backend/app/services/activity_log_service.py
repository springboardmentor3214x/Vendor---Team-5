"""Persistence helpers for the existing activity_logs table.

The current table deliberately has a small schema.  Additional activity context is
stored in its description field until a dedicated metadata migration is supplied.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from app.models.activity_log import ActivityLog


def _description(
    details: dict[str, Any] | str | None,
    related_entity_type: str | None,
    related_entity_id: int | None,
    ip_address: str | None,
) -> str | None:
    if details is None and related_entity_type is None and related_entity_id is None and ip_address is None:
        return None
    payload: dict[str, Any] = {}
    if isinstance(details, dict):
        payload.update(details)
    elif details:
        payload["details"] = details
    if related_entity_type is not None:
        payload["related_entity_type"] = related_entity_type
    if related_entity_id is not None:
        payload["related_entity_id"] = related_entity_id
    if ip_address is not None:
        payload["ip_address"] = ip_address
    return json.dumps(payload, default=str, sort_keys=True)[:500]


def record_activity_log(
    db: Any,
    user_id: int | None,
    action: str,
    module_name: str,
    related_entity_type: str | None = None,
    related_entity_id: int | None = None,
    ip_address: str | None = None,
    details: dict[str, Any] | str | None = None,
) -> ActivityLog:
    """Create an activity record using the currently migrated table columns."""
    if db is None:
        raise ValueError("A database session is required to record activity.")
    if not action or not action.strip() or not module_name or not module_name.strip():
        raise ValueError("action and module_name are required.")
    log = ActivityLog(
        user_id=user_id,
        action=action.strip(),
        module=module_name.strip(),
        description=_description(details, related_entity_type, related_entity_id, ip_address),
        created_at=datetime.utcnow(),
    )
    try:
        db.add(log)
        db.commit()
        db.refresh(log)
    except Exception:
        db.rollback()
        raise
    return log


def list_activity_logs(db: Any, filters: dict[str, Any] | None = None) -> list[ActivityLog]:
    """Return activity history, optionally filtered by migrated table fields."""
    if db is None:
        return []
    try:
        query = db.query(ActivityLog)
        for name, value in (filters or {}).items():
            if value is not None and name in {"id", "user_id", "action", "module"}:
                query = query.filter(getattr(ActivityLog, name) == value)
        return list(query.order_by(ActivityLog.created_at.desc()).all() or [])
    except Exception:
        return []
