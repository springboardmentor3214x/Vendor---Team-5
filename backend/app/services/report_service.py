"""DB-backed Module 6 report preparation; format rendering remains an API concern."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app.models.certification import Certification
from app.models.compliance import ComplianceRecord
from app.models.contract import Contract
from app.models.vendor_document import VendorDocument
from app.services.notification_service import get_user_notifications


def _value(value: Any) -> Any:
    return value.isoformat() if isinstance(value, (date, datetime)) else value


def _filter(query: Any, model: Any, filters: dict[str, Any] | None) -> Any:
    for key, value in (filters or {}).items():
        if value is not None and hasattr(model, key):
            query = query.filter(getattr(model, key) == value)
    return query


def _rows(db: Any, model: Any, filters: dict[str, Any] | None = None) -> list[Any]:
    """Read available ORM rows without turning missing tables into fake reports."""
    if db is None:
        return []
    try:
        return list(_filter(db.query(model), model, filters).all() or [])
    except Exception:
        return []


def _row(item: Any, names: tuple[str, ...]) -> dict[str, Any]:
    return {name: _value(getattr(item, name, None)) for name in names}


def generate_contract_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [_row(row, ("id", "vendor_id", "contract_number", "contract_title", "status", "start_date",
                       "end_date", "contract_value")) for row in _rows(db, Contract, filters)]


def generate_compliance_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [_row(row, ("id", "vendor_id", "compliance_type", "status", "verification_date", "remarks"))
            for row in _rows(db, ComplianceRecord, filters)]


def generate_vendor_document_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [_row(row, ("id", "vendor_id", "document_type", "file_name", "content_type", "uploaded_at"))
            for row in _rows(db, VendorDocument, filters)]


def generate_notification_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """No model means no fabricated notification report rows."""
    user_id = (filters or {}).get("user_id")
    if user_id is None:
        return []
    return [_notification_row(item) for item in get_user_notifications(db, user_id)]


def _notification_row(item: Any) -> dict[str, Any]:
    return {name: _value(getattr(item, name)) for name in
            ("id", "user_id", "title", "message", "notification_type", "related_entity_id", "is_read", "created_at")
            if hasattr(item, name)}


def export_report_data(db: Any, report_type: str, format: str = "csv", filters: dict[str, Any] | None = None) -> dict[str, Any]:
    generators = {"contract": generate_contract_report, "compliance": generate_compliance_report,
                  "vendor_document": generate_vendor_document_report, "notification": generate_notification_report}
    if report_type not in generators:
        raise ValueError(f"Unsupported report type: {report_type}")
    if format.lower() not in {"csv", "pdf", "excel"}:
        raise ValueError(f"Unsupported export format: {format}")
    rows = generators[report_type](db, filters)
    return {"report_type": report_type, "format": format.lower(), "rows": rows,
            "metadata": {"row_count": len(rows), "status": "prepared"}}
