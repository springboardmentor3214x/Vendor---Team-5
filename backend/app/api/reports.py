import csv
import io
from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, normalize_user_role
from app.core.database import get_db
from app.models.user import User
from app.schemas.report import ReportChartOut, ReportPreviewOut
from app.services import report_service
from app.services import export_service

router = APIRouter(prefix="/reports", tags=["Reports"])
_REPORT_ROLES = {"Administrator", "Procurement Manager", "Supply Chain Manager", "Finance Officer", "Auditor"}
_REPORT_TYPES = {"vendor-performance": "vendor_performance", "procurement": "procurement_summary", "contracts": "contract", "compliance": "compliance", "vendor-documents": "vendor_document", "purchase-orders": "purchase_order", "executive-summary": "executive_summary", "communications": "communication", "activity-logs": "activity_log", "dashboard-analytics": "dashboard_analytics"}


def _require(current_user: User) -> None:
    if normalize_user_role(current_user) not in _REPORT_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


def _filters(report_type: str, start_date: date | None, end_date: date | None, department: str | None, vendor_id: int | None, vendor_name: str | None, vendor_category: str | None, procurement_status: str | None, purchase_order_status: str | None, contract_status: str | None, compliance_status: str | None, reliability_level: str | None) -> dict[str, Any]:
    """Validate and forward only filters the report service supports."""
    if reliability_level is not None and report_type != "vendor_performance":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reliability_level is supported only for vendor-performance reports",
        )
    values = locals().copy()
    values.pop("report_type")
    return {key: value for key, value in values.items() if value is not None}


def _rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    raw = result["rows"]
    return raw if isinstance(raw, list) else [raw]


def _csv(rows: list[dict[str, Any]], filename: str) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()) if rows else ["message"])
    writer.writeheader(); writer.writerows(rows or [{"message": "No matching records"}]); output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


_SORT_FIELDS = {
    "vendor_performance": {"vendor_name", "reliability_score", "overall_performance_score", "evaluation_date"},
    "procurement_summary": {"request_number", "department", "estimated_budget", "approval_status", "request_date"},
    "purchase_order": {"purchase_order_number", "vendor_name", "purchase_date", "order_value", "current_status"},
    "contract": {"contract_number", "vendor_name", "status", "end_date", "contract_value"},
    "compliance": {"vendor_id", "status", "verification_date", "vendor_compliance_percentage"},
}


def _sorted(rows: list[dict[str, Any]], report_type: str, sort_by: str | None, sort_order: str) -> list[dict[str, Any]]:
    if sort_order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="sort_order must be asc or desc")
    if sort_by is None:
        return rows
    if sort_by not in _SORT_FIELDS.get(report_type, set()):
        raise HTTPException(status_code=400, detail=f"sort_by is not supported for {report_type}")
    return sorted(rows, key=lambda row: (row.get(sort_by) is None, row.get(sort_by)), reverse=sort_order == "desc")


@router.get("/")
def list_reports(current_user: User = Depends(get_current_user)):
    _require(current_user)
    # ``/{report_key}/export`` supports all of these formats. Keep discovery in
    # sync so API consumers do not incorrectly treat PDF/XLSX as unavailable.
    return {"items": [{"key": key, "title": key.replace("-", " ").title(), "formats": ["json", "csv", "xlsx", "pdf"], "status": "ready"} for key in _REPORT_TYPES], "generated_at": datetime.utcnow()}


@router.get("/{report_key}/preview", response_model=ReportPreviewOut)
def preview_report(report_key: str, start_date: date | None = Query(None), end_date: date | None = Query(None), department: str | None = None, vendor_id: int | None = None, vendor_name: str | None = None, vendor_category: str | None = None, procurement_status: str | None = None, purchase_order_status: str | None = None, contract_status: str | None = None, compliance_status: str | None = None, reliability_level: str | None = None, sort_by: str | None = Query(None), sort_order: str = Query("asc"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user); report_type = _REPORT_TYPES.get(report_key)
    if not report_type: raise HTTPException(status_code=404, detail="Unsupported report type")
    result = report_service.export_report_data(db, report_type, filters=_filters(report_type, start_date, end_date, department, vendor_id, vendor_name, vendor_category, procurement_status, purchase_order_status, contract_status, compliance_status, reliability_level))
    return ReportPreviewOut(report_type=report_type, rows=_sorted(_rows(result), report_type, sort_by, sort_order), metadata=result["metadata"])


@router.get("/{report_key}/charts", response_model=ReportChartOut)
def report_charts(report_key: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user); report_type = _REPORT_TYPES.get(report_key)
    if not report_type: raise HTTPException(status_code=404, detail="Unsupported report type")
    try: data = report_service.get_report_chart_data(db, report_type)
    except ValueError as exc: data = {"series": [], "reason": str(exc)}
    return ReportChartOut(report_type=report_type, data=data)


@router.get("/{report_key}/export")
def export_report(report_key: str, format: str = Query("csv"), start_date: date | None = Query(None), end_date: date | None = Query(None), department: str | None = None, vendor_id: int | None = None, vendor_name: str | None = None, vendor_category: str | None = None, procurement_status: str | None = None, purchase_order_status: str | None = None, contract_status: str | None = None, compliance_status: str | None = None, reliability_level: str | None = None, sort_by: str | None = Query(None), sort_order: str = Query("asc"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user); report_type = _REPORT_TYPES.get(report_key)
    if not report_type: raise HTTPException(status_code=404, detail="Unsupported report type")
    applied_filters = _filters(report_type, start_date, end_date, department, vendor_id, vendor_name, vendor_category, procurement_status, purchase_order_status, contract_status, compliance_status, reliability_level)
    try: result = report_service.export_report_data(db, report_type, format="csv", filters=applied_filters)
    except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc
    rows = _sorted(_rows(result), report_type, sort_by, sort_order)
    filename = report_key.replace("-", "_")
    if format == "csv": return _csv(rows, f"{filename}.csv")
    if format == "xlsx":
        return StreamingResponse(iter([export_service.build_excel(report_type, rows, applied_filters)]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{filename}.xlsx"'})
    if format == "pdf":
        try: chart_data = report_service.get_report_chart_data(db, report_type)
        except ValueError: chart_data = {"series": [], "reason": "No chart mapping for this report type"}
        return StreamingResponse(iter([export_service.build_pdf(report_type, rows, applied_filters, chart_data)]), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{filename}.pdf"'})
    raise HTTPException(status_code=400, detail="format must be csv, xlsx, or pdf")


@router.get("/contracts/expiring", response_model=ReportPreviewOut)
def expiring_contract_report(window: int = Query(30), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user)
    if window not in {30, 60, 90}:
        raise HTTPException(status_code=400, detail="window must be 30, 60, or 90 days")
    result = report_service.export_report_data(db, "contract")
    today = date.today()
    rows = [row for row in _rows(result) if isinstance(row.get("end_date"), str) and 0 <= (date.fromisoformat(row["end_date"][:10]) - today).days <= window]
    return ReportPreviewOut(report_type="contract", rows=rows, metadata={"row_count": len(rows), "window_days": window, "status": "prepared"})


# Stable Module 5/6 aliases used by the existing frontend.
# These are intentionally CSV-only compatibility routes. They retain their
# established no-query-parameter contract; consumers needing filtering,
# sorting, PDF, or XLSX must use ``/{report_key}/export`` or ``/preview``.
@router.get("/vendor-performance")
def export_vendor_performance_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user); return _csv(_rows(report_service.export_report_data(db, "vendor_performance")), "vendor_performance_report.csv")

@router.get("/procurement")
def export_procurement_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user); return _csv(_rows(report_service.export_report_data(db, "procurement_summary")), "procurement_report.csv")

@router.get("/contracts")
def export_contract_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user); return _csv(_rows(report_service.export_report_data(db, "contract")), "contract_report.csv")

@router.get("/compliance")
def export_compliance_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user); return _csv(_rows(report_service.export_report_data(db, "compliance")), "compliance_report.csv")

@router.get("/vendor-documents")
def export_vendor_document_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user); return _csv(_rows(report_service.export_report_data(db, "vendor_document")), "vendor_document_report.csv")

@router.get("/purchase-orders")
def export_purchase_order_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user); return _csv(_rows(report_service.export_report_data(db, "purchase_order")), "purchase_order_report.csv")

@router.get("/executive-summary", response_model=ReportPreviewOut)
def executive_summary_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user); result = report_service.export_report_data(db, "executive_summary")
    return ReportPreviewOut(report_type="executive_summary", rows=_rows(result), metadata=result["metadata"])
