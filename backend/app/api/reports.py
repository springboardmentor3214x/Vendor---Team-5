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

router = APIRouter(prefix="/reports", tags=["Reports"])
_REPORT_ROLES = {"Administrator", "Procurement Manager", "Supply Chain Manager", "Finance Officer", "Auditor"}
_REPORT_TYPES = {"vendor-performance": "vendor_performance", "procurement": "procurement_summary", "contracts": "contract", "compliance": "compliance", "vendor-documents": "vendor_document", "purchase-orders": "purchase_order", "executive-summary": "executive_summary", "communications": "communication", "activity-logs": "activity_log", "dashboard-analytics": "dashboard_analytics"}


def _require(current_user: User) -> None:
    if normalize_user_role(current_user) not in _REPORT_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


def _filters(start_date: date | None, end_date: date | None, department: str | None, vendor_id: int | None, vendor_name: str | None, vendor_category: str | None, procurement_status: str | None, purchase_order_status: str | None, contract_status: str | None, compliance_status: str | None, reliability_level: str | None) -> dict[str, Any]:
    return {key: value for key, value in locals().items() if value is not None}


def _rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    raw = result["rows"]
    return raw if isinstance(raw, list) else [raw]


def _csv(rows: list[dict[str, Any]], filename: str) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()) if rows else ["message"])
    writer.writeheader(); writer.writerows(rows or [{"message": "No matching records"}]); output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/")
def list_reports(current_user: User = Depends(get_current_user)):
    _require(current_user)
    return {"items": [{"key": key, "title": key.replace("-", " ").title(), "formats": ["json", "csv"], "status": "ready"} for key in _REPORT_TYPES], "generated_at": datetime.utcnow()}


@router.get("/{report_key}/preview", response_model=ReportPreviewOut)
def preview_report(report_key: str, start_date: date | None = Query(None), end_date: date | None = Query(None), department: str | None = None, vendor_id: int | None = None, vendor_name: str | None = None, vendor_category: str | None = None, procurement_status: str | None = None, purchase_order_status: str | None = None, contract_status: str | None = None, compliance_status: str | None = None, reliability_level: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user); report_type = _REPORT_TYPES.get(report_key)
    if not report_type: raise HTTPException(status_code=404, detail="Unsupported report type")
    result = report_service.export_report_data(db, report_type, filters=_filters(start_date, end_date, department, vendor_id, vendor_name, vendor_category, procurement_status, purchase_order_status, contract_status, compliance_status, reliability_level))
    return ReportPreviewOut(report_type=report_type, rows=_rows(result), metadata=result["metadata"])


@router.get("/{report_key}/charts", response_model=ReportChartOut)
def report_charts(report_key: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user); report_type = _REPORT_TYPES.get(report_key)
    if not report_type: raise HTTPException(status_code=404, detail="Unsupported report type")
    try: data = report_service.get_report_chart_data(db, report_type)
    except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ReportChartOut(report_type=report_type, data=data)


@router.get("/{report_key}/export")
def export_report(report_key: str, format: str = Query("csv"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user); report_type = _REPORT_TYPES.get(report_key)
    if not report_type: raise HTTPException(status_code=404, detail="Unsupported report type")
    try: result = report_service.export_report_data(db, report_type, format=format)
    except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc
    if result["metadata"].get("status") == "unavailable":
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=result["metadata"]["message"])
    return _csv(_rows(result), f"{report_key.replace('-', '_')}.csv")


# Stable Module 5/6 aliases used by the existing frontend.
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
