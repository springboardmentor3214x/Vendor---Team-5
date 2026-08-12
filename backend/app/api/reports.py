import io
from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])

_REPORT_ROLES = {
    "Administrator",
    "Procurement Manager",
    "Supply Chain Manager",
    "Finance Officer",
    "Auditor",
}


def _role_name(current_user: User) -> str | None:
    role = getattr(current_user, "role", None)
    return getattr(role, "name", role)


def _require_report_access(current_user: User) -> None:
    if _role_name(current_user) not in _REPORT_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


def _export_response(report_type: str, rows: list[dict], format: str = "csv"):
    fmt = format.lower()
    if fmt not in {"csv", "pdf"}:
        raise HTTPException(status_code=400, detail="Only csv and pdf export formats are currently supported")
    filename = f"{report_type}_report.{'pdf' if fmt == 'pdf' else 'csv'}"

    if fmt == "pdf":
        pdf_bytes = report_service.render_pdf_report(report_type.replace("-", " ").title(), rows)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    else:
        csv_str = report_service.render_excel_csv_report(rows)
        return StreamingResponse(
            io.StringIO(csv_str),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )


# The fixed-path endpoints below remain for backward compatibility.  Their
# original narrow filters are deliberately unchanged; frontend clients that
# require matching preview/export filters should use the generic endpoints
# added at the end of this module.
_REPORT_GENERATORS = {
    "vendor-performance": report_service.generate_vendor_performance_report,
    "procurement": report_service.generate_procurement_summary_report,
    "purchase-orders": report_service.generate_purchase_order_report,
    "compliance": report_service.generate_compliance_report,
    "contracts": report_service.generate_contract_report,
    "vendor-documents": report_service.generate_vendor_document_report,
    "executive-summary": report_service.generate_executive_summary_report,
}

_REPORT_SORT_FIELDS = {
    "vendor-performance": {"vendor_id", "total_completed_orders", "on_time_delivery_rate", "average_quality_score", "average_response_time", "overall_performance_score", "performance_status", "reliability_score", "risk_level", "evaluation_date"},
    "procurement": {"procurement_request_id", "request_number", "title", "department", "vendor_id", "estimated_budget", "priority", "approval_status", "request_date", "po_status", "total_cost"},
    "purchase-orders": {"purchase_order_id", "purchase_order_number", "vendor_name", "purchase_date", "delivery_date", "order_value", "current_status", "invoice_status"},
    "compliance": {"id", "vendor_id", "compliance_type", "status", "verification_date", "expired_certifications", "vendor_compliance_percentage"},
    "contracts": {"id", "vendor_id", "contract_number", "contract_title", "status", "start_date", "end_date", "contract_value", "days_to_expiry"},
    "vendor-documents": {"id", "vendor_id", "document_type", "file_name", "uploaded_at"},
    "executive-summary": set(),
}

_STATUS_FIELD_BY_REPORT = {
    "vendor-performance": "performance_status",
    "procurement": "approval_status",
    "purchase-orders": "po_status",
    "compliance": "status",
    "contracts": "status",
}


def _parse_iso_date(value: str | None, parameter_name: str) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"{parameter_name} must use YYYY-MM-DD") from exc


def _normalized_report_filters(
    report_key: str,
    *,
    start_date: str | None,
    end_date: str | None,
    department: str | None,
    vendor_id: int | None,
    category_id: int | None,
    status_value: str | None,
    reliability_level: str | None,
) -> tuple[dict, dict]:
    """Return service-safe filters and the matching response-row filters."""
    if report_key not in _REPORT_GENERATORS:
        raise HTTPException(status_code=404, detail="Unknown report type")
    if category_id is not None:
        raise HTTPException(status_code=400, detail="categoryId is not supported by the current persisted report rows")
    if reliability_level is not None and report_key != "vendor-performance":
        raise HTTPException(status_code=400, detail="reliabilityLevel is supported only for vendor-performance reports")
    if department is not None and report_key != "procurement":
        raise HTTPException(status_code=400, detail="department is supported only for procurement reports")
    if status_value is not None and report_key not in _STATUS_FIELD_BY_REPORT:
        raise HTTPException(status_code=400, detail="status is not supported by this report type")
    if vendor_id is not None and report_key == "executive-summary":
        raise HTTPException(status_code=400, detail="vendorId is not supported by executive-summary reports")

    start = _parse_iso_date(start_date, "startDate")
    end = _parse_iso_date(end_date, "endDate")
    if start and end and start > end:
        raise HTTPException(status_code=400, detail="startDate cannot be after endDate")

    service_filters: dict = {}
    if vendor_id is not None:
        service_filters["vendor_id"] = vendor_id
    if department is not None:
        service_filters["department"] = department
    if status_value is not None:
        service_filters[_STATUS_FIELD_BY_REPORT[report_key]] = status_value

    return service_filters, {
        "start_date": start,
        "end_date": end,
        "department": department,
        "vendor_id": vendor_id,
        "status": status_value,
        "reliability_level": reliability_level,
    }


def _row_date(row: dict) -> date | None:
    for key in ("request_date", "purchase_date", "verification_date", "start_date", "evaluation_date", "uploaded_at"):
        value = row.get(key)
        if value is None:
            continue
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
            except ValueError:
                continue
    return None


def _apply_row_filters_and_sort(
    report_key: str,
    rows: list[dict],
    filters: dict,
    sort_by: str | None,
    sort_order: str,
) -> list[dict]:
    filtered = list(rows)
    if filters["vendor_id"] is not None:
        filtered = [row for row in filtered if row.get("vendor_id") == filters["vendor_id"]]
    if filters["department"] is not None:
        filtered = [row for row in filtered if row.get("department") == filters["department"]]
    if filters["status"] is not None:
        status_field = _STATUS_FIELD_BY_REPORT.get(report_key)
        if status_field:
            filtered = [row for row in filtered if str(row.get(status_field, "")).lower() == filters["status"].lower()]
    if filters["reliability_level"] is not None:
        filtered = [row for row in filtered if str(row.get("risk_level", "")).lower() == filters["reliability_level"].lower()]
    if filters["start_date"] or filters["end_date"]:
        def in_range(row: dict) -> bool:
            row_date = _row_date(row)
            if row_date is None:
                return False
            return (filters["start_date"] is None or row_date >= filters["start_date"]) and (filters["end_date"] is None or row_date <= filters["end_date"])
        filtered = [row for row in filtered if in_range(row)]

    if sort_order.lower() not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="sortOrder must be asc or desc")
    if sort_by is not None:
        if sort_by not in _REPORT_SORT_FIELDS[report_key]:
            raise HTTPException(status_code=400, detail="sortBy is not supported for this report type")

        def sort_value(row: dict):
            value = row.get(sort_by)
            if value is None:
                return (1, "")
            if isinstance(value, (int, float)):
                return (0, value)
            try:
                return (0, float(value))
            except (TypeError, ValueError):
                return (0, str(value).lower())

        filtered.sort(
            key=sort_value,
            reverse=sort_order.lower() == "desc",
        )
    return filtered


def _report_rows(
    report_key: str,
    db: Session,
    *,
    start_date: str | None,
    end_date: str | None,
    department: str | None,
    vendor_id: int | None,
    category_id: int | None,
    status_value: str | None,
    reliability_level: str | None,
    sort_by: str | None,
    sort_order: str,
) -> list[dict]:
    service_filters, row_filters = _normalized_report_filters(
        report_key,
        start_date=start_date,
        end_date=end_date,
        department=department,
        vendor_id=vendor_id,
        category_id=category_id,
        status_value=status_value,
        reliability_level=reliability_level,
    )
    raw_rows = _REPORT_GENERATORS[report_key](db, service_filters or None)
    rows = raw_rows if isinstance(raw_rows, list) else [raw_rows]
    return _apply_row_filters_and_sort(report_key, rows, row_filters, sort_by, sort_order)


@router.get("/")
def list_reports(current_user: User = Depends(get_current_user)):
    """List available Module 10 reporting modules and metadata."""
    _require_report_access(current_user)
    return {
        "items": [
            {"key": "vendor-performance", "title": "Vendor Performance Report", "formats": ["json", "csv", "pdf"], "status": "ready"},
            {"key": "procurement", "title": "Procurement Summary Report", "formats": ["json", "csv", "pdf"], "status": "ready"},
            {"key": "purchase-orders", "title": "Purchase Order Report", "formats": ["json", "csv", "pdf"], "status": "ready"},
            {"key": "compliance", "title": "Compliance Status Report", "formats": ["json", "csv", "pdf"], "status": "ready"},
            {"key": "contracts", "title": "Contract Status Report", "formats": ["json", "csv", "pdf"], "status": "ready"},
            {"key": "executive-summary", "title": "Executive Summary Report", "formats": ["json", "pdf"], "status": "ready"},
            {"key": "vendor-documents", "title": "Vendor Document Report", "formats": ["json", "csv", "pdf"], "status": "ready"},
        ],
        "generated_at": datetime.utcnow()
    }


@router.get("/vendor-performance")
def get_vendor_performance_report_endpoint(
    format: str = Query("json", description="json, csv, or pdf"),
    category_id: Optional[int] = Query(None, alias="categoryId"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Vendor Performance Evaluation Report endpoint."""
    _require_report_access(current_user)
    filters = {"category_id": category_id} if category_id else None
    rows = report_service.generate_vendor_performance_report(db, filters)

    if format.lower() == "json":
        return {"report_type": "vendor-performance", "rows": rows, "total_rows": len(rows)}
    return _export_response("vendor_performance", rows, format)


@router.get("/procurement")
def get_procurement_report_endpoint(
    format: str = Query("json", description="json, csv, or pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Procurement Summary Activity and Spending Report endpoint."""
    _require_report_access(current_user)
    rows = report_service.generate_procurement_summary_report(db)

    if format.lower() == "json":
        return {"report_type": "procurement", "rows": rows, "total_rows": len(rows)}
    return _export_response("procurement", rows, format)


@router.get("/purchase-orders")
def get_purchase_order_report_endpoint(
    format: str = Query("json", description="json, csv, or pdf"),
    vendor_id: Optional[int] = Query(None, alias="vendorId"),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Purchase Order Transaction Report endpoint."""
    _require_report_access(current_user)
    filters = {}
    if vendor_id:
        filters["vendor_id"] = vendor_id
    if status:
        filters["purchase_order_status"] = status

    rows = report_service.generate_purchase_order_report(db, filters)

    if format.lower() == "json":
        return {"report_type": "purchase-orders", "rows": rows, "total_rows": len(rows)}
    return _export_response("purchase_orders", rows, format)


@router.get("/compliance")
def get_compliance_report_endpoint(
    format: str = Query("json", description="json, csv, or pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compliance Status Verification Report endpoint."""
    _require_report_access(current_user)
    rows = report_service.generate_compliance_report(db)

    if format.lower() == "json":
        return {"report_type": "compliance", "rows": rows, "total_rows": len(rows)}
    return _export_response("compliance", rows, format)


@router.get("/contracts")
def get_contract_report_endpoint(
    format: str = Query("json", description="json, csv, or pdf"),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Contract Status and Renewal Expiry Report endpoint."""
    _require_report_access(current_user)
    filters = {"status": status} if status else None
    rows = report_service.generate_contract_report(db, filters)

    if format.lower() == "json":
        return {"report_type": "contracts", "rows": rows, "total_rows": len(rows)}
    return _export_response("contract", rows, format)


@router.get("/contracts/expiring")
def get_expiring_contracts_report(
    window: int = Query(30, ge=30, le=90, description="Expiry window in days: 30, 60, or 90"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return persisted contract-report rows expiring within 30, 60, or 90 days."""
    _require_report_access(current_user)
    if window not in {30, 60, 90}:
        raise HTTPException(status_code=400, detail="window must be one of 30, 60, or 90")
    rows = report_service.generate_contract_report(db)
    expiring = [
        row for row in rows
        if row.get("days_to_expiry") is not None and 0 <= row["days_to_expiry"] <= window
    ]
    return {"report_type": "contracts-expiring", "window_days": window, "rows": expiring, "total_rows": len(expiring)}


@router.get("/executive-summary")
def get_executive_summary_report_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Executive High-Level Business Insights Summary Report endpoint."""
    _require_report_access(current_user)
    return report_service.generate_executive_summary_report(db)


@router.get("/vendor-documents")
def get_vendor_document_report_endpoint(
    format: str = Query("json", description="json, csv, or pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Vendor Document and Certificate Report endpoint."""
    _require_report_access(current_user)
    rows = report_service.generate_vendor_document_report(db)

    if format.lower() == "json":
        return {"report_type": "vendor-documents", "rows": rows, "total_rows": len(rows)}
    return _export_response("vendor_document", rows, format)


@router.get("/{report_key}/preview")
def preview_report_endpoint(
    report_key: str,
    start_date: str | None = Query(None, alias="startDate"),
    end_date: str | None = Query(None, alias="endDate"),
    department: str | None = Query(None),
    vendor_id: int | None = Query(None, alias="vendorId"),
    category_id: int | None = Query(None, alias="categoryId"),
    status_value: str | None = Query(None, alias="status"),
    reliability_level: str | None = Query(None, alias="reliabilityLevel"),
    sort_by: str | None = Query(None, alias="sortBy"),
    sort_order: str = Query("asc", alias="sortOrder"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Preview the exact persisted rows and filter/sort contract used by export."""
    _require_report_access(current_user)
    rows = _report_rows(
        report_key, db, start_date=start_date, end_date=end_date, department=department,
        vendor_id=vendor_id, category_id=category_id, status_value=status_value,
        reliability_level=reliability_level, sort_by=sort_by, sort_order=sort_order,
    )
    return {"report_type": report_key, "rows": rows, "total_rows": len(rows)}


@router.get("/{report_key}/export")
def export_report_endpoint(
    report_key: str,
    format: str = Query("csv", description="csv or pdf"),
    start_date: str | None = Query(None, alias="startDate"),
    end_date: str | None = Query(None, alias="endDate"),
    department: str | None = Query(None),
    vendor_id: int | None = Query(None, alias="vendorId"),
    category_id: int | None = Query(None, alias="categoryId"),
    status_value: str | None = Query(None, alias="status"),
    reliability_level: str | None = Query(None, alias="reliabilityLevel"),
    sort_by: str | None = Query(None, alias="sortBy"),
    sort_order: str = Query("asc", alias="sortOrder"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export the same filtered and sorted rows exposed by the preview route."""
    _require_report_access(current_user)
    rows = _report_rows(
        report_key, db, start_date=start_date, end_date=end_date, department=department,
        vendor_id=vendor_id, category_id=category_id, status_value=status_value,
        reliability_level=reliability_level, sort_by=sort_by, sort_order=sort_order,
    )
    return _export_response(report_key.replace("-", "_"), rows, format)
