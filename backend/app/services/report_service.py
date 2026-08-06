"""DB-backed Module 6 report preparation; format rendering remains an API concern."""

from __future__ import annotations

from collections import defaultdict
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
from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.services.dashboard_service import (
    get_communication_dashboard_summary, get_contract_dashboard_summary,
    get_dashboard_chart_data, get_delivery_status_dashboard, get_procurement_dashboard_summary,
    get_procurement_cost_analysis, get_vendor_performance_dashboard,
)
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
        rows = list(_filter(db.query(model), model, filters).all() or [])
        return [row for row in rows if _matches_filters(row, filters)]
    except Exception:
        return []


def _row(item: Any, names: tuple[str, ...]) -> dict[str, Any]:
    return {name: _value(getattr(item, name, None)) for name in names}


def _day(value: Any) -> date | None:
    return value.date() if isinstance(value, datetime) else value if isinstance(value, date) else None


def _matches_filters(row: Any, filters: dict[str, Any] | None) -> bool:
    """Apply cross-report aliases only when the row has supporting fields."""
    aliases = {"procurement_status": "approval_status", "purchase_order_status": "po_status",
               "contract_status": "status", "compliance_status": "status"}
    for name, value in (filters or {}).items():
        if value is None:
            continue
        if name in {"start_date", "end_date"}:
            candidate = next((_day(getattr(row, field, None)) for field in
                              ("request_date", "po_date", "created_at", "verification_date", "start_date")
                              if _day(getattr(row, field, None)) is not None), None)
            if candidate and ((name == "start_date" and candidate < _day(value)) or
                              (name == "end_date" and candidate > _day(value))):
                return False
            continue
        if name == "reliability_score_min" and hasattr(row, "reliability_score") and getattr(row, "reliability_score") < value:
            return False
        if name == "reliability_score_max" and hasattr(row, "reliability_score") and getattr(row, "reliability_score") > value:
            return False
        field = aliases.get(name, name)
        if hasattr(row, field) and getattr(row, field) != value:
            return False
    return True


def _vendor_map(db: Any) -> dict[int, Any]:
    return {getattr(row, "id", None): row for row in _rows(db, Vendor)}


def _vendor_matches(vendor: Any, filters: dict[str, Any] | None) -> bool:
    if vendor is None:
        return not (filters or {}).get("vendor_name") and not (filters or {}).get("vendor_category")
    name, category = (filters or {}).get("vendor_name"), (filters or {}).get("vendor_category")
    if name and getattr(vendor, "company_name", None) != name:
        return False
    category_name = getattr(getattr(vendor, "category", None), "name", None)
    return not category or category_name == category


def generate_contract_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    vendors, today, result = _vendor_map(db), date.today(), []
    for contract in _rows(db, Contract, filters):
        row = _row(contract, ("id", "vendor_id", "contract_number", "contract_title", "status", "start_date",
                              "end_date", "contract_value"))
        vendor = vendors.get(getattr(contract, "vendor_id", None))
        if not _vendor_matches(vendor, filters):
            continue
        if vendor is not None:
            row.update({"vendor_name": getattr(vendor, "company_name", None), "contract_type": getattr(contract, "contract_type", None),
                        "contract_manager": getattr(contract, "responsible_manager", None), "renewal_status": getattr(contract, "status", None),
                        "compliance_status": "Verified" if getattr(contract, "compliance_verified", False) else "Pending"})
            end = _day(getattr(contract, "end_date", None))
            row["expiry_window_days"] = (end - today).days if end else None
        result.append(row)
    return result


def generate_compliance_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    certifications = _rows(db, Certification, filters)
    expired_by_vendor = defaultdict(int)
    for certification in certifications:
        expiry = _day(getattr(certification, "expiry_date", None))
        if expiry and expiry < date.today():
            expired_by_vendor[getattr(certification, "vendor_id", None)] += 1
    records = _rows(db, ComplianceRecord, filters)
    totals = defaultdict(int)
    compliant = defaultdict(int)
    for record in records:
        vendor_id = getattr(record, "vendor_id", None)
        totals[vendor_id] += 1
        compliant[vendor_id] += getattr(record, "status", None) == "Compliant"
    result = []
    for record in records:
        row = _row(record, ("id", "vendor_id", "compliance_type", "status", "verification_date", "remarks"))
        row["expired_certifications"] = expired_by_vendor.get(getattr(record, "vendor_id", None), 0)
        row["pending_compliance_activity"] = getattr(record, "status", None) == "Pending Verification"
        vendor_id = getattr(record, "vendor_id", None)
        row["vendor_compliance_percentage"] = round(compliant[vendor_id] / totals[vendor_id] * 100, 2) if totals[vendor_id] else 0
        result.append(row)
    return result


def generate_vendor_document_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [_row(row, ("id", "vendor_id", "document_type", "file_name", "content_type", "uploaded_at"))
            for row in _rows(db, VendorDocument, filters)]


def generate_notification_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """No model means no fabricated notification report rows."""
    user_id = (filters or {}).get("user_id")
    if user_id is None:
        return []
    return [_notification_row(item) for item in get_user_notifications(db, user_id, filters)]


def generate_communication_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [_row(row, ("id", "sender_id", "vendor_id", "procurement_request_id", "subject", "message", "created_at"))
            for row in _rows(db, Communication, filters)]


def generate_activity_log_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [_row(row, ("id", "user_id", "module", "action", "description", "created_at"))
            for row in _rows(db, ActivityLog, filters)]


def generate_vendor_performance_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Prepare rows from persisted performance records, with reliability when present."""
    reliability_by_vendor = {getattr(row, "vendor_id", None): row for row in _rows(db, VendorReliability, filters)}
    vendors = _vendor_map(db)
    rows = []
    for record in _rows(db, PerformanceRecord, filters):
        reliability = reliability_by_vendor.get(getattr(record, "vendor_id", None))
        row = _row(record, ("id", "vendor_id", "total_completed_orders", "on_time_delivery_rate",
                            "delayed_delivery_count", "average_quality_score", "average_response_time",
                            "average_service_rating_score", "overall_performance_score", "performance_status",
                            "evaluation_date"))
        row["reliability_score"] = _value(getattr(reliability, "reliability_score", None))
        row["risk_level"] = _value(getattr(reliability, "risk_level", None))
        vendor = vendors.get(getattr(record, "vendor_id", None))
        if not _vendor_matches(vendor, filters):
            continue
        if vendor is not None:
            row["vendor_name"] = getattr(vendor, "company_name", None)
            row["vendor_category"] = getattr(getattr(vendor, "category", None), "name", None)
            row["communication_activity_metric"] = _value(getattr(reliability, "communication_score", None))
            row["issue_resolution_performance"] = _value(getattr(reliability, "issue_resolution_score", None))
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


def generate_procurement_report(db: Any, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return actual procurement aggregates, with optional department/date filters."""
    requests = _rows(db, ProcurementRequest, filters)
    orders = _rows(db, PurchaseOrder, filters)
    departments: dict[str, dict[str, float | int]] = defaultdict(lambda: {"requests": 0, "estimated_budget": 0.0})
    for request in requests:
        department = getattr(request, "department", None)
        if department:
            departments[department]["requests"] += 1
            departments[department]["estimated_budget"] += float(getattr(request, "estimated_budget", 0) or 0)
    monthly: dict[str, float] = defaultdict(float)
    for order in orders:
        day = _day(getattr(order, "po_date", None))
        if day:
            monthly[day.strftime("%Y-%m")] += float(getattr(order, "total_cost", 0) or 0)
    return {"total_procurement_requests": len(requests),
            "approved_requests": sum(getattr(row, "approval_status", None) == "Approved" for row in requests),
            "generated_purchase_orders": len(orders), "completed_procurements": sum(getattr(row, "po_status", None) == "Delivered" for row in orders),
            "total_procurement_expenditure": round(sum(float(getattr(row, "total_cost", 0) or 0) for row in orders), 2),
            "department_summary": [{"department": name, **values} for name, values in sorted(departments.items())],
            "monthly_trends": [{"month": name, "total": round(total, 2)} for name, total in sorted(monthly.items())]}


def generate_purchase_order_report(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    vendors, requests = _vendor_map(db), {getattr(row, "id", None): row for row in _rows(db, ProcurementRequest)}
    invoices = {getattr(row, "purchase_order_id", None): row for row in _rows(db, Invoice)}
    result = []
    for order in _rows(db, PurchaseOrder, filters):
        request, vendor, invoice = requests.get(getattr(order, "procurement_request_id", None)), vendors.get(getattr(order, "vendor_id", None)), invoices.get(getattr(order, "id", None))
        if not _vendor_matches(vendor, filters):
            continue
        result.append({"purchase_order_id": getattr(order, "id", None), "purchase_order_number": getattr(order, "po_number", None),
                       "vendor_name": getattr(vendor, "company_name", None), "procurement_category": getattr(request, "product_category", None),
                       "purchase_date": _value(getattr(order, "po_date", None)), "delivery_date": _value(getattr(order, "actual_delivery_date", None)),
                       "order_value": getattr(order, "total_cost", None), "current_status": getattr(order, "po_status", None),
                       "invoice_status": getattr(invoice, "payment_status", None), "completion_date": _value(getattr(order, "actual_delivery_date", None))})
    return result


def generate_executive_summary_report(db: Any, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    vendors = _rows(db, Vendor, filters)
    procurement = generate_procurement_report(db, filters)
    performance = get_vendor_performance_dashboard(db, filters)
    compliance = generate_compliance_report(db, filters)
    compliant = sum(row.get("status") == "Compliant" for row in compliance)
    return {"total_registered_vendors": len(vendors), "active_vendors": sum(getattr(row, "vendor_status", None) == "Active" for row in vendors),
            "procurement_spending": procurement["total_procurement_expenditure"],
            "vendor_reliability_distribution": get_report_chart_data(db, "reliability", filters)["reliability_distribution"],
            "top_performing_vendors": performance["best_performing_vendors"],
            "delayed_deliveries": get_delivery_status_dashboard(db, filters)["delayed_deliveries"],
            "contracts_near_expiry": get_contract_dashboard_summary(db)["expiring_soon_contracts"],
            "procurement_completion_rate": round(procurement["completed_procurements"] / procurement["generated_purchase_orders"] * 100, 2) if procurement["generated_purchase_orders"] else 0,
            "compliance_percentage": round(compliant / len(compliance) * 100, 2) if compliance else 0,
            "monthly_procurement_trends": procurement["monthly_trends"]}


def generate_communication_history_report(db: Any, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    messages = generate_communication_report(db, filters)
    activities = generate_activity_log_report(db, {"module": "Communication"})
    return {"interaction_history": messages, "vendor_linked_messages": sum(row["vendor_id"] is not None for row in messages),
            "procurement_linked_messages": sum(row["procurement_request_id"] is not None for row in messages),
            "activity_summary": {"count": len(activities), "activities": activities}}


def generate_dashboard_analytics_report(db: Any, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"procurement_analytics": get_procurement_dashboard_summary(db, filters),
            "vendor_analytics": get_vendor_performance_dashboard(db, filters),
            "contract_tracking": get_contract_dashboard_summary(db),
            "communication_summary": get_communication_dashboard_summary(db, (filters or {}).get("vendor_id"))}


def _notification_row(item: Any) -> dict[str, Any]:
    return {name: _value(getattr(item, name)) for name in
            ("id", "user_id", "title", "message", "description", "notification_type", "related_module",
             "related_entity_id", "priority", "delivery_method", "is_read", "created_at")
            if hasattr(item, name)}


def get_report_chart_data(db: Any, report_type: str, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return chart-ready facts without rendering charts or inventing series values."""
    charts = get_dashboard_chart_data(db, filters)
    procurement = get_procurement_dashboard_summary(db, filters)
    status_counts: dict[str, int] = defaultdict(int)
    for row in _rows(db, ProcurementRequest, filters):
        if getattr(row, "approval_status", None):
            status_counts[row.approval_status] += 1
    supported = {"executive_summary", "procurement", "procurement_summary", "vendor_performance", "contract", "compliance", "dashboard_analytics", "reliability"}
    if report_type not in supported:
        raise ValueError(f"Unsupported chart report type: {report_type}")
    return {"report_type": report_type, "monthly_procurement_trends": procurement["monthly_procurement_volume"],
            "monthly_procurement_expenses": charts["monthly_procurement_expenses"],
            "vendor_reliability_distribution": charts["reliability_distribution"],
            "reliability_distribution": charts["reliability_distribution"],
            "contract_status_distribution": charts["contract_status_distribution"],
            "procurement_status_distribution": [{"status": key, "count": value} for key, value in sorted(status_counts.items())],
            "spending_by_vendor": get_procurement_cost_analysis(db, filters)["spending_by_vendor"],
            "spending_by_category": get_procurement_cost_analysis(db, filters)["spending_by_category"],
            "spending_by_project": get_procurement_cost_analysis(db, filters)["spending_by_project"]}


def export_report_data(
    db: Any, report_type: str, format: str = "csv", filters: dict[str, Any] | None = None, *, export_format: str | None = None
) -> dict[str, Any]:
    """Prepare structured export data; PDF/Excel rendering needs an external library."""
    generators = {"contract": generate_contract_report, "compliance": generate_compliance_report,
                  "vendor_document": generate_vendor_document_report, "notification": generate_notification_report,
                  "vendor_performance": generate_vendor_performance_report,
                  "procurement_summary": generate_procurement_summary_report,
                  "procurement": generate_procurement_report, "purchase_order": generate_purchase_order_report,
                  "executive_summary": generate_executive_summary_report, "communication": generate_communication_report,
                  "communication_history": generate_communication_history_report, "activity_log": generate_activity_log_report,
                  "dashboard_analytics": generate_dashboard_analytics_report}
    if report_type not in generators:
        raise ValueError(f"Unsupported report type: {report_type}")
    selected_format = (export_format or format).lower()
    if selected_format not in {"csv", "pdf", "excel"}:
        raise ValueError(f"Unsupported export format: {selected_format}")
    rows = generators[report_type](db, filters)
    row_count = len(rows) if isinstance(rows, list) else 1
    result = {"report_type": report_type, "format": selected_format, "rows": rows,
              "metadata": {"row_count": row_count, "status": "prepared"}}
    if selected_format in {"pdf", "excel"}:
        result["metadata"] = {"row_count": row_count, "status": "unavailable",
                               "message": f"{selected_format.upper()} rendering requires a configured export library."}
    return result
