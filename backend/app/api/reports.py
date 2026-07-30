import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
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


@router.get("/")
def list_reports(current_user: User = Depends(get_current_user)):
    _require_report_access(current_user)
    return {"items": [
        {"key": "vendor-performance", "title": "Vendor Performance Report", "format": "csv", "status": "ready"},
        {"key": "procurement", "title": "Procurement Summary Report", "format": "csv", "status": "ready"},
        {"key": "contracts", "title": "Contract Report", "format": "csv", "status": "ready"},
        {"key": "compliance", "title": "Compliance Status Report", "format": "csv", "status": "ready"},
        {"key": "vendor-documents", "title": "Vendor Document Report", "format": "csv", "status": "ready"},
    ], "generated_at": datetime.utcnow()}


def csv_download_response(rows: list[dict], filename: str) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()) if rows else ["message"])
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/vendor-performance")
def export_vendor_performance_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_report_access(current_user)
    report = report_service.export_report_data(db, "vendor_performance", format="csv")
    return csv_download_response(report["rows"], "vendor_performance_report.csv")


@router.get("/procurement")
def export_procurement_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_report_access(current_user)
    report = report_service.export_report_data(db, "procurement_summary", format="csv")
    return csv_download_response(report["rows"], "procurement_report.csv")


@router.get("/contracts")
def export_contract_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_report_access(current_user)
    report = report_service.export_report_data(db, "contract", format="csv")
    return csv_download_response(report["rows"], "contract_report.csv")


@router.get("/compliance")
def export_compliance_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_report_access(current_user)
    report = report_service.export_report_data(db, "compliance", format="csv")
    return csv_download_response(report["rows"], "compliance_report.csv")


@router.get("/vendor-documents")
def export_vendor_document_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_report_access(current_user)
    report = report_service.export_report_data(db, "vendor_document", format="csv")
    return csv_download_response(report["rows"], "vendor_document_report.csv")
