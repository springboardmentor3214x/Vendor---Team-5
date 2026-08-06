from datetime import date, datetime
from types import SimpleNamespace

from app.models.compliance import ComplianceRecord
from app.models.contract import Contract
from app.models.invoice import Invoice
from app.models.performance import PerformanceRecord
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.reliability import VendorReliability
from app.models.vendor import Vendor
from app.services.report_service import (
    export_report_data, generate_executive_summary_report, generate_procurement_report,
    generate_purchase_order_report, generate_vendor_performance_report, get_report_chart_data,
)


class Query:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, _condition):
        return self

    def all(self):
        return self.rows


class Db:
    def __init__(self, rows):
        self.rows = rows

    def query(self, model):
        return Query(self.rows.get(model, []))


def make_db():
    vendor = SimpleNamespace(id=1, company_name="Acme", vendor_status="Active", category=SimpleNamespace(name="Metal"))
    request = SimpleNamespace(id=2, vendor_id=1, request_number="PR-2", department="Operations", product_category="Steel",
                              approval_status="Approved", estimated_budget=120.0, request_date=date(2026, 8, 2))
    order = SimpleNamespace(id=3, procurement_request_id=2, vendor_id=1, po_number="PO-3", po_status="Delivered", total_cost=100.0,
                            po_date=datetime(2026, 8, 3), expected_delivery_date=None, actual_delivery_date=datetime(2026, 8, 4))
    return Db({Vendor: [vendor], ProcurementRequest: [request], PurchaseOrder: [order],
               Invoice: [SimpleNamespace(purchase_order_id=3, payment_status="Paid")],
               PerformanceRecord: [SimpleNamespace(id=4, vendor_id=1, total_completed_orders=1, on_time_delivery_rate=95.0,
                   delayed_delivery_count=0, average_quality_score=90.0, average_response_time=60.0,
                   average_service_rating_score=92.0, overall_performance_score=91.0, performance_status="Excellent", evaluation_date=None)],
               VendorReliability: [SimpleNamespace(vendor_id=1, reliability_score=88.0, risk_level="Low Risk", communication_score=80.0, issue_resolution_score=85.0)],
               Contract: [SimpleNamespace(id=5, vendor_id=1, contract_number="C-5", contract_title="Steel", status="Active",
                   start_date=date(2026, 1, 1), end_date=date(2026, 12, 1), contract_value=500.0, contract_type="Supply",
                   responsible_manager="Manager", compliance_verified=True)],
               ComplianceRecord: [SimpleNamespace(id=6, vendor_id=1, compliance_type="GST", status="Compliant", verification_date=None, remarks=None)]})


def test_module10_reports_aggregate_existing_model_shaped_rows():
    db = make_db()
    vendor_report = generate_vendor_performance_report(db, {"vendor_name": "Acme"})
    assert vendor_report[0]["vendor_name"] == "Acme"
    assert vendor_report[0]["communication_activity_metric"] == 80.0
    procurement = generate_procurement_report(db)
    assert procurement["total_procurement_expenditure"] == 100.0
    assert procurement["department_summary"][0]["department"] == "Operations"
    order = generate_purchase_order_report(db)[0]
    assert order["invoice_status"] == "Paid"
    assert generate_executive_summary_report(db)["total_registered_vendors"] == 1


def test_module10_export_and_chart_helpers_do_not_render_unconfigured_files():
    db = make_db()
    charts = get_report_chart_data(db, "procurement")
    assert charts["spending_by_category"] == [{"category": "Steel", "total": 100.0}]
    pdf = export_report_data(db, "procurement", export_format="pdf")
    assert pdf["metadata"]["status"] == "unavailable"
    csv = export_report_data(db, "purchase_order", "csv")
    assert csv["metadata"] == {"row_count": 1, "status": "prepared"}
