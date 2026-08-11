"""Read-only dashboard aggregation from the currently available ORM models."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any

from app.models.certification import Certification
from app.models.compliance import ComplianceRecord
from app.models.contract import Contract
from app.models.vendor_document import VendorDocument
from app.models.communication import Communication
from app.models.activity_log import ActivityLog
from app.models.invoice import Invoice
from app.models.order_tracking import OrderTracking
from app.models.performance import PerformanceRecord
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.reliability import PerformanceTrend, VendorReliability
from app.models.user import User
from app.models.vendor import Vendor
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


def _filtered_rows(db: Any, model: Any, filters: dict[str, Any] | None = None) -> list[Any]:
    """Apply only filters represented on a model; unsupported filters are ignored."""
    rows = _rows(db, model)
    return [row for row in rows if all(
        value is None or not hasattr(row, name) or getattr(row, name) == value
        for name, value in (filters or {}).items()
    )]


def _month(value: date | datetime | None) -> str | None:
    day = _day(value)
    return day.strftime("%Y-%m") if day else None


def _sum(rows: list[Any], field: str) -> float:
    return round(sum(float(getattr(row, field, 0) or 0) for row in rows), 2)


def _group_total(rows: list[Any], key_name: str, value_name: str) -> list[dict[str, Any]]:
    totals: dict[str, float] = defaultdict(float)
    for row in rows:
        key = getattr(row, key_name, None)
        if key is not None:
            totals[str(key)] += float(getattr(row, value_name, 0) or 0)
    return [{"label": key, "total": round(value, 2)} for key, value in sorted(totals.items())]


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


def get_communication_dashboard_summary(db: Any, vendor_id: int | None = None) -> dict[str, int]:
    """Summarize only persisted communications; discussion/read metrics need schema support."""
    rows = _rows(db, Communication)
    if vendor_id is not None:
        rows = [row for row in rows if getattr(row, "vendor_id", None) == vendor_id]
    return {"total_messages": len(rows), "vendor_linked_messages": sum(
        getattr(row, "vendor_id", None) is not None for row in rows), "procurement_linked_messages": sum(
        getattr(row, "procurement_request_id", None) is not None for row in rows)}


def get_procurement_dashboard_summary(db: Any, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    """Aggregate persisted procurement requests and purchase orders."""
    requests = _filtered_rows(db, ProcurementRequest, filters)
    orders = _filtered_rows(db, PurchaseOrder, filters)
    request_months: dict[str, int] = defaultdict(int)
    departments: dict[str, int] = defaultdict(int)
    for request in requests:
        if getattr(request, "department", None):
            departments[request.department] += 1
        if month := _month(getattr(request, "request_date", None)):
            request_months[month] += 1
    return {
        "total_procurement_requests": len(requests),
        "pending_approvals": sum(getattr(row, "approval_status", None) == "Pending" for row in requests),
        "active_purchase_orders": sum(getattr(row, "po_status", None) == "Issued" for row in orders),
        "completed_orders": sum(getattr(row, "po_status", None) == "Delivered" for row in orders),
        "cancelled_orders": sum(getattr(row, "po_status", None) == "Cancelled" for row in orders),
        "requests_by_department": [{"department": name, "count": count} for name, count in sorted(departments.items())],
        "monthly_procurement_volume": [{"month": month, "count": count} for month, count in sorted(request_months.items())],
        "procurement_cost_summary": {"total_purchase_order_cost": _sum(orders, "total_cost"),
                                     "total_estimated_budget": _sum(requests, "estimated_budget")},
    }


def get_procurement_overview(db: Any, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    today = date.today()
    requests = _filtered_rows(db, ProcurementRequest, filters)
    orders = _filtered_rows(db, PurchaseOrder, filters)
    current_year = [row for row in orders if _day(getattr(row, "po_date", None)) and getattr(row, "po_date").year == today.year]
    prior_year = [row for row in orders if _day(getattr(row, "po_date", None)) and getattr(row, "po_date").year == today.year - 1]
    prior_spend = _sum(prior_year, "total_cost")
    return {
        "today_procurement_requests": sum(_day(getattr(row, "request_date", None)) == today for row in requests),
        "weekly_completed_purchase_orders": sum(
            getattr(row, "po_status", None) == "Delivered" and today - timedelta(days=6) <=
            (_day(getattr(row, "actual_delivery_date", None)) or _day(getattr(row, "po_date", None)) or date.min) <= today
            for row in orders),
        "monthly_procurement_spending": _sum([row for row in orders if _day(getattr(row, "po_date", None)) and
                                                getattr(row, "po_date").year == today.year and getattr(row, "po_date").month == today.month], "total_cost"),
        # A percentage is undefined without a prior-year baseline.
        "yearly_procurement_growth_percent": round((_sum(current_year, "total_cost") - prior_spend) / prior_spend * 100, 2)
        if prior_spend else None,
    }


def get_active_purchase_orders_summary(db: Any, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    today = date.today()
    vendors = {getattr(row, "id", None): row for row in _rows(db, Vendor)}
    requests = {getattr(row, "id", None): row for row in _rows(db, ProcurementRequest)}
    rows = []
    for order in _filtered_rows(db, PurchaseOrder, filters):
        if getattr(order, "po_status", None) != "Issued":
            continue
        expected = _day(getattr(order, "expected_delivery_date", None))
        if expected and expected < today:
            indicator = "Delayed"
        elif expected and expected <= today + timedelta(days=7):
            indicator = "Due Soon"
        else:
            indicator = "On Track"
        vendor = vendors.get(getattr(order, "vendor_id", None))
        request = requests.get(getattr(order, "procurement_request_id", None))
        rows.append({"purchase_order_id": getattr(order, "id", None), "purchase_order_number": getattr(order, "po_number", None),
                     "vendor_name": getattr(vendor, "company_name", None), "procurement_category": getattr(request, "product_category", None),
                     "status": getattr(order, "po_status", None), "expected_delivery_date": expected,
                     "deadline_indicator": indicator,
                     # The model has created_by but no assigned-manager field/name relationship.
                     "assigned_procurement_manager": None})
    return rows


def get_vendor_performance_dashboard(db: Any, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    vendors = {getattr(row, "id", None): row for row in _filtered_rows(db, Vendor, filters)}
    reliability = {getattr(row, "vendor_id", None): row for row in _filtered_rows(db, VendorReliability, filters)}
    rows = []
    for record in _filtered_rows(db, PerformanceRecord, filters):
        vendor_id = getattr(record, "vendor_id", None)
        if filters and filters.get("vendor_id") is not None and vendor_id != filters["vendor_id"]:
            continue
        score = getattr(record, "overall_performance_score", None)
        reliability_row = reliability.get(vendor_id)
        rows.append({"vendor_id": vendor_id, "vendor_name": getattr(vendors.get(vendor_id), "company_name", None),
                     "overall_performance_rating": score, "delivery_accuracy": getattr(record, "on_time_delivery_rate", None),
                     "product_quality_score": getattr(record, "average_quality_score", None),
                     "communication_efficiency": getattr(reliability_row, "communication_score", None),
                     "issue_resolution": getattr(reliability_row, "issue_resolution_score", None),
                     "average_service_rating": getattr(record, "average_service_rating_score", None),
                     "reliability_score": getattr(reliability_row, "reliability_score", None),
                     "performance_status": getattr(record, "performance_status", None)})
    ranked = sorted(rows, key=lambda row: row["overall_performance_rating"] if row["overall_performance_rating"] is not None else -1, reverse=True)
    return {"vendors": ranked,
            "best_performing_vendors": [row for row in ranked if (row["overall_performance_rating"] or 0) >= 80],
            "vendors_requiring_improvement": [row for row in ranked if (row["overall_performance_rating"] or 0) < 70 or row["performance_status"] == "Poor"]}


def get_procurement_cost_analysis(db: Any, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    orders = _filtered_rows(db, PurchaseOrder, filters)
    vendors = {getattr(row, "id", None): row for row in _rows(db, Vendor)}
    requests = {getattr(row, "id", None): row for row in _rows(db, ProcurementRequest)}
    by_vendor: dict[str, float] = defaultdict(float)
    by_category: dict[str, float] = defaultdict(float)
    by_department: dict[str, float] = defaultdict(float)
    by_month: dict[str, float] = defaultdict(float)
    for order in orders:
        cost = float(getattr(order, "total_cost", 0) or 0)
        vendor = vendors.get(getattr(order, "vendor_id", None))
        request = requests.get(getattr(order, "procurement_request_id", None))
        by_vendor[getattr(vendor, "company_name", None) or str(getattr(order, "vendor_id", None))] += cost
        if request:
            if getattr(request, "product_category", None): by_category[request.product_category] += cost
            if getattr(request, "department", None): by_department[request.department] += cost
        if month := _month(getattr(order, "po_date", None)): by_month[month] += cost
    rows = lambda values, key: [{key: name, "total": round(value, 2)} for name, value in sorted(values.items())]
    return {"spending_by_vendor": rows(by_vendor, "vendor"), "spending_by_category": rows(by_category, "category"),
            "monthly_expenses": rows(by_month, "month"), "department_spending": rows(by_department, "department")}


def get_delivery_status_dashboard(db: Any, filters: dict[str, Any] | None = None) -> dict[str, int]:
    tracking = _filtered_rows(db, OrderTracking, filters)
    vendor_id = (filters or {}).get("vendor_id")
    if vendor_id is not None:
        vendor_order_ids = {getattr(row, "id", None) for row in _filtered_rows(db, PurchaseOrder, {"vendor_id": vendor_id})}
        tracking = [row for row in tracking if getattr(row, "purchase_order_id", None) in vendor_order_ids]
    # Order tracking is the authoritative delivery workflow when its table has rows.
    rows = tracking or _filtered_rows(db, PurchaseOrder, filters)
    statuses = [getattr(row, "delivery_status", None) or getattr(row, "po_status", None) for row in rows]
    return {"on_time_deliveries": sum(status in {"On-Time Delivery", "Early Delivery"} for status in statuses),
            "delayed_deliveries": sum(status in {"Delayed", "Delayed Delivery"} for status in statuses),
            "delivered_orders": sum(status == "Delivered" for status in statuses),
            "pending_shipments": sum(status in {"Awaiting Shipment", "In Transit", "Issued"} for status in statuses),
            "completed_deliveries": sum(status == "Completed" for status in statuses)}


def get_vendor_dashboard_summary(db: Any, vendor_id: int) -> dict[str, Any]:
    performance = next((row for row in _rows(db, PerformanceRecord) if getattr(row, "vendor_id", None) == vendor_id), None)
    reliability = next((row for row in _rows(db, VendorReliability) if getattr(row, "vendor_id", None) == vendor_id), None)
    orders = [row for row in _rows(db, PurchaseOrder) if getattr(row, "vendor_id", None) == vendor_id]
    contracts = [row for row in _rows(db, Contract) if getattr(row, "vendor_id", None) == vendor_id]
    order_ids = {getattr(row, "id", None) for row in orders}
    invoices = [row for row in _rows(db, Invoice) if getattr(row, "purchase_order_id", None) in order_ids]
    communications = [row for row in _rows(db, Communication) if getattr(row, "vendor_id", None) == vendor_id]
    vendor_tracking = [row for row in _rows(db, OrderTracking) if getattr(row, "purchase_order_id", None) in order_ids]
    vendor = next((row for row in _rows(db, Vendor) if getattr(row, "id", None) == vendor_id), None)
    user_ids = {getattr(vendor, name, None) for name in ("user_id", "account_id", "contact_user_id") if vendor is not None}
    user_ids.update(getattr(getattr(vendor, name, None), "id", None) for name in ("user", "account", "contact_user") if vendor is not None)
    user_ids.discard(None)
    if not user_ids and vendor is not None and getattr(vendor, "email", None):
        user_ids.update(getattr(row, "id", None) for row in _rows(db, User) if getattr(row, "email", None) == vendor.email)
    recent_notifications = []
    for user_id in user_ids:
        recent_notifications.extend(get_user_notifications(db, user_id))
    delivery = get_delivery_status_dashboard(db, {"vendor_id": vendor_id}) if vendor_tracking else {
        "pending_shipments": sum(getattr(row, "po_status", None) == "Issued" for row in orders)}
    return {"overall_performance_score": getattr(performance, "overall_performance_score", None),
            "reliability_score": getattr(reliability, "reliability_score", None),
            "active_purchase_orders": sum(getattr(row, "po_status", None) == "Issued" for row in orders),
            "completed_orders": sum(getattr(row, "po_status", None) == "Delivered" for row in orders),
            "contract_status": {status: sum(getattr(row, "status", None) == status for row in contracts)
                                for status in sorted({getattr(row, "status", None) for row in contracts if getattr(row, "status", None)})},
            "pending_deliveries": delivery["pending_shipments"],
            "recent_communications": sorted(communications, key=lambda row: getattr(row, "created_at", datetime.min), reverse=True)[:5],
            "payment_status": {status: sum(getattr(row, "payment_status", None) == status for row in invoices)
                               for status in sorted({getattr(row, "payment_status", None) for row in invoices if getattr(row, "payment_status", None)})},
            "recent_notifications": sorted(recent_notifications, key=lambda row: getattr(row, "created_at", datetime.min), reverse=True)[:5],
    }


def get_admin_dashboard_summary(db: Any) -> dict[str, Any]:
    users = _rows(db, User)
    vendors = _rows(db, Vendor)
    return {"total_users": len(users), "active_users": sum(bool(getattr(row, "is_active", False)) for row in users),
            "total_vendors": len(vendors), "procurement_statistics": get_procurement_dashboard_summary(db),
            "vendor_analytics": get_vendor_performance_dashboard(db), "compliance_monitoring": get_compliance_dashboard_summary(db),
            "contract_status": get_contract_dashboard_summary(db), "system_activity_count": len(_rows(db, ActivityLog))}


def get_dashboard_chart_data(db: Any, filters: dict[str, Any] | None = None) -> dict[str, list[dict[str, Any]]]:
    costs = get_procurement_cost_analysis(db, filters)
    requests = _filtered_rows(db, ProcurementRequest, filters)
    contracts = _filtered_rows(db, Contract, filters)
    reliability = _filtered_rows(db, VendorReliability, filters)
    trends = _filtered_rows(db, PerformanceTrend, filters)
    category_counts: dict[str, int] = defaultdict(int)
    contract_counts: dict[str, int] = defaultdict(int)
    risk_counts: dict[str, int] = defaultdict(int)
    for row in requests:
        if getattr(row, "product_category", None): category_counts[row.product_category] += 1
    for row in contracts:
        if getattr(row, "status", None): contract_counts[row.status] += 1
    for row in reliability:
        if getattr(row, "risk_level", None): risk_counts[row.risk_level] += 1
    return {"monthly_procurement_expenses": costs["monthly_expenses"],
            "vendor_performance_trends": [{"vendor_id": getattr(row, "vendor_id", None), "year": getattr(row, "year", None),
                                             "month": getattr(row, "month", None), "reliability_score": getattr(row, "reliability_score", None)}
                                            for row in sorted(trends, key=lambda row: (getattr(row, "year", 0), getattr(row, "month", 0)))],
            "procurement_category_distribution": [{"category": name, "count": count} for name, count in sorted(category_counts.items())],
            "contract_status_distribution": [{"status": name, "count": count} for name, count in sorted(contract_counts.items())],
            "reliability_distribution": [{"risk_level": name, "count": count} for name, count in sorted(risk_counts.items())]}


def get_module6_dashboard_summary(db: Any, user_id: int | None = None) -> dict[str, dict[str, int]]:
    return {"contracts": get_contract_dashboard_summary(db), "compliance": get_compliance_dashboard_summary(db),
            "documents": get_document_dashboard_summary(db), "notifications": get_notification_dashboard_summary(db, user_id)}
