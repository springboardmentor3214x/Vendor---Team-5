import csv
import io
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/")
def list_reports():
    return {"items": [
        {"key": "vendor-performance", "title": "Vendor Performance Report", "format": "csv", "status": "ready"},
        {"key": "procurement", "title": "Procurement Summary Report", "format": "csv", "status": "ready"},
        {"key": "compliance", "title": "Compliance Status Report", "format": "csv", "status": "ready"},
    ], "generated_at": datetime.utcnow()}


def csv_download_response(rows: list[dict], filename: str) -> StreamingResponse:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()) if rows else ["message"])
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/vendor-performance")
def export_vendor_performance_report():
    return csv_download_response([
        {"vendor_id": 1, "vendor_name": "ABC Supplies", "overall_score": 88.5, "performance_status": "Excellent"},
        {"vendor_id": 2, "vendor_name": "Prime Industrial", "overall_score": 74.0, "performance_status": "Good"},
    ], "vendor_performance_report.csv")


@router.get("/procurement")
def export_procurement_report():
    return csv_download_response([
        {"request_id": 101, "department": "Operations", "status": "Approved", "total_amount": 25000.0},
        {"request_id": 102, "department": "Maintenance", "status": "Pending", "total_amount": 9800.0},
    ], "procurement_report.csv")


@router.get("/compliance")
def export_compliance_report():
    return csv_download_response([
        {"vendor_id": 1, "vendor_name": "ABC Supplies", "compliance_verified": True, "contract_status": "Active"},
        {"vendor_id": 2, "vendor_name": "Prime Industrial", "compliance_verified": False, "contract_status": "Expiring Soon"},
    ], "compliance_report.csv")
