"""Read-only dashboard aggregation from the currently available ORM models."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app.models.certification import Certification
from app.models.compliance import ComplianceRecord
from app.models.contract import Contract
from app.models.vendor_document import VendorDocument
from app.services.contract_compliance_service import is_contract_expiring_soon
from app.services.notification_service import get_unread_notifications, get_user_notifications


def _day(value: date | datetime | None) -> date | None:
    return value.date() if isinstance(value, datetime) else value


def _rows(db: Any, model: Any) -> list[Any]:
    """Return query results, treating unavailable optional tables as empty."""
    if db is None:
        return []
    try:
        return list(db.query(model).all() or [])
    except Exception:
        return []


def get_contract_dashboard_summary(db: Any) -> dict[str, int]:
    today = date.today()
    contracts = _rows(db, Contract)
    active = expired = expiring = 0
    for contract in contracts:
        end_date = _day(getattr(contract, "end_date", None))
        start_date = _day(getattr(contract, "start_date", None))
        if end_date is not None and end_date < today:
            expired += 1
        elif start_date is not None and start_date <= today:
            active += 1
            if end_date is not None and is_contract_expiring_soon(end_date, today):
                expiring += 1
    return {"total_contracts": len(contracts), "active_contracts": active,
            "expired_contracts": expired, "expiring_soon_contracts": expiring}


def get_compliance_dashboard_summary(db: Any) -> dict[str, int]:
    records = _rows(db, ComplianceRecord)
    return {"total_compliance_records": len(records),
            "compliant_count": sum(getattr(row, "status", None) == "Compliant" for row in records),
            "non_compliant_count": sum(getattr(row, "status", None) == "Non-Compliant" for row in records),
            "pending_count": sum(getattr(row, "status", None) == "Pending Verification" for row in records),
            "expired_count": sum(getattr(row, "status", None) == "Expired" for row in records)}


def get_document_dashboard_summary(db: Any) -> dict[str, int]:
    today = date.today()
    certifications = _rows(db, Certification)
    documents = _rows(db, VendorDocument)
    return {"total_documents": len(documents), "total_certifications": len(certifications),
            "expired_certifications": sum((_day(getattr(row, "expiry_date", None)) or today) < today for row in certifications),
            "expiring_soon_certifications": sum(
                bool(_day(getattr(row, "expiry_date", None))) and is_contract_expiring_soon(_day(getattr(row, "expiry_date", None)), today)
                for row in certifications)}


def get_notification_dashboard_summary(db: Any, user_id: int | None = None) -> dict[str, int]:
    notifications = get_user_notifications(db, user_id) if user_id is not None else []
    unread = get_unread_notifications(db, user_id) if user_id is not None else []
    return {"total_notifications": len(notifications), "unread_notifications": len(unread)}


def get_module6_dashboard_summary(db: Any, user_id: int | None = None) -> dict[str, dict[str, int]]:
    return {"contracts": get_contract_dashboard_summary(db), "compliance": get_compliance_dashboard_summary(db),
            "documents": get_document_dashboard_summary(db), "notifications": get_notification_dashboard_summary(db, user_id)}
