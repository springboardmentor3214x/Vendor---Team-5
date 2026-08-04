"""DB-backed Module 6 report preparation; format rendering remains an API concern."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app.models.certification import Certification
from app.models.compliance import ComplianceRecord
from app.models.contract import Contract
from app.models.vendor_document import VendorDocument
from app.models.performance import PerformanceRecord
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.reliability import VendorReliability
from app.models.communication import Communication
from app.models.activity_log import ActivityLog
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


def generate_communication_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [_row(row, ("id", "sender_id", "vendor_id", "procurement_request_id", "subject", "message", "created_at"))
            for row in _rows(db, Communication, filters)]


def generate_activity_log_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [_row(row, ("id", "user_id", "module", "action", "description", "created_at"))
            for row in _rows(db, ActivityLog, filters)]


def generate_vendor_performance_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Prepare rows from persisted performance records, with reliability when present."""
    reliability_by_vendor = {getattr(row, "vendor_id", None): row for row in _rows(db, VendorReliability)}
    rows = []
    for record in _rows(db, PerformanceRecord, filters):
        reliability = reliability_by_vendor.get(getattr(record, "vendor_id", None))
        row = _row(record, ("id", "vendor_id", "total_completed_orders", "on_time_delivery_rate",
                            "delayed_delivery_count", "average_quality_score", "average_response_time",
                            "average_service_rating_score", "overall_performance_score", "performance_status",
                            "evaluation_date"))
        row["reliability_score"] = _value(getattr(reliability, "reliability_score", None))
        row["risk_level"] = _value(getattr(reliability, "risk_level", None))
        rows.append(row)
    return rows


def generate_procurement_summary_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Prepare actual procurement-request rows and their matching purchase-order facts."""
    purchase_orders = {getattr(row, "procurement_request_id", None): row for row in _rows(db, PurchaseOrder)}
    rows = []
    for request in _rows(db, ProcurementRequest, filters):
        order = purchase_orders.get(getattr(request, "id", None))
        row = _row(request, ("id", "request_number", "title", "department", "vendor_id", "quantity",
                             "estimated_budget", "priority", "approval_status", "request_date", "approved_date"))
        row.update(_row(order, ("id", "po_number", "po_status", "total_cost", "expected_delivery_date",
                                "actual_delivery_date")) if order is not None else {
            "id": None, "po_number": None, "po_status": None, "total_cost": None,
            "expected_delivery_date": None, "actual_delivery_date": None,
        })
        # Avoid ambiguous IDs in exports while retaining the historical request id field.
        row["purchase_order_id"] = row.pop("id") if order is not None else None
        row["procurement_request_id"] = getattr(request, "id", None)
        rows.append(row)
    return rows


def _notification_row(item: Any) -> dict[str, Any]:
    return {name: _value(getattr(item, name)) for name in
            ("id", "user_id", "title", "message", "notification_type", "related_entity_id", "is_read", "created_at")
            if hasattr(item, name)}


def export_report_data(db: Any, report_type: str, format: str = "csv", filters: dict[str, Any] | None = None) -> dict[str, Any]:
    generators = {"contract": generate_contract_report, "compliance": generate_compliance_report,
                  "vendor_document": generate_vendor_document_report, "notification": generate_notification_report,
                  "vendor_performance": generate_vendor_performance_report,
                  "procurement_summary": generate_procurement_summary_report,
                  "communication": generate_communication_report, "activity_log": generate_activity_log_report}
    if report_type not in generators:
        raise ValueError(f"Unsupported report type: {report_type}")
    if format.lower() not in {"csv", "pdf", "excel"}:
        raise ValueError(f"Unsupported export format: {format}")
    rows = generators[report_type](db, filters)
    return {"report_type": report_type, "format": format.lower(), "rows": rows,
            "metadata": {"row_count": len(rows), "status": "prepared"}}
