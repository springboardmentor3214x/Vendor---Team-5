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
    filename = f"{report_type}_report.{'pdf' if fmt == 'pdf' else 'csv'}"

    if fmt == "pdf":
        pdf_bytes = report_service.render_pdf_report(report_type.replace("-", " ").title(), rows)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    else:  # csv or excel
        csv_str = report_service.render_excel_csv_report(rows)
        return StreamingResponse(
            io.StringIO(csv_str),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )


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
    format: str = Query("json", description="json, csv, excel, or pdf"),
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
    format: str = Query("json", description="json, csv, excel, or pdf"),
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
    format: str = Query("json", description="json, csv, excel, or pdf"),
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
    format: str = Query("json", description="json, csv, excel, or pdf"),
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
    format: str = Query("json", description="json, csv, excel, or pdf"),
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
    format: str = Query("json", description="json, csv, excel, or pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Vendor Document and Certificate Report endpoint."""
    _require_report_access(current_user)
    rows = report_service.generate_vendor_document_report(db)

    if format.lower() == "json":
        return {"report_type": "vendor-documents", "rows": rows, "total_rows": len(rows)}
    return _export_response("vendor_document", rows, format)
