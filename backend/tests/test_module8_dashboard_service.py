from datetime import date, datetime, timedelta
from types import SimpleNamespace

from app.models.activity_log import ActivityLog
from app.models.communication import Communication
from app.models.contract import Contract
from app.models.invoice import Invoice
from app.models.order_tracking import OrderTracking
from app.models.performance import PerformanceRecord
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.reliability import PerformanceTrend, VendorReliability
from app.models.user import User
from app.models.vendor import Vendor
from app.services.dashboard_service import (
    get_active_purchase_orders_summary, get_admin_dashboard_summary, get_dashboard_chart_data,
    get_delivery_status_dashboard, get_procurement_cost_analysis, get_procurement_dashboard_summary,
    get_procurement_overview, get_vendor_dashboard_summary, get_vendor_performance_dashboard,
)


class Query:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class Db:
    def __init__(self, rows):
        self.rows = rows

    def query(self, model):
        return Query(self.rows.get(model, []))


def make_db():
    today = date.today()
    request = SimpleNamespace(id=10, department="Operations", product_category="Steel", approval_status="Pending",
                              estimated_budget=150.0, request_date=today, vendor_id=1)
    order = SimpleNamespace(id=20, procurement_request_id=10, vendor_id=1, po_number="PO-20", po_status="Issued",
                            total_cost=125.0, po_date=datetime(today.year, today.month, 2), expected_delivery_date=today + timedelta(days=2),
                            actual_delivery_date=None)
    vendor = SimpleNamespace(id=1, company_name="Acme Supplies", is_active=True)
    performance = SimpleNamespace(vendor_id=1, overall_performance_score=85.0, on_time_delivery_rate=96.0,
                                  average_quality_score=91.0, average_service_rating_score=88.0, performance_status="Excellent")
    reliability = SimpleNamespace(vendor_id=1, reliability_score=82.0, communication_score=80.0,
                                  issue_resolution_score=75.0, risk_level="Low Risk")
    return Db({ProcurementRequest: [request], PurchaseOrder: [order], Vendor: [vendor], PerformanceRecord: [performance],
               VendorReliability: [reliability], Contract: [SimpleNamespace(vendor_id=1, status="Active", start_date=today, end_date=today + timedelta(days=30))],
               OrderTracking: [SimpleNamespace(purchase_order_id=20, delivery_status="In Transit")],
               Invoice: [SimpleNamespace(purchase_order_id=20, payment_status="Pending")],
               Communication: [SimpleNamespace(vendor_id=1, created_at=datetime.now())], User: [SimpleNamespace(is_active=True)],
               ActivityLog: [SimpleNamespace()], PerformanceTrend: [SimpleNamespace(vendor_id=1, year=today.year, month=today.month, reliability_score=82.0)]})


def test_procurement_analytics_aggregate_persisted_model_shaped_rows():
    db = make_db()
    summary = get_procurement_dashboard_summary(db)
    assert summary["total_procurement_requests"] == 1
    assert summary["pending_approvals"] == 1
    assert summary["active_purchase_orders"] == 1
    assert summary["procurement_cost_summary"]["total_purchase_order_cost"] == 125.0
    assert get_procurement_overview(db)["today_procurement_requests"] == 1
    assert get_procurement_cost_analysis(db)["spending_by_vendor"] == [{"vendor": "Acme Supplies", "total": 125.0}]


def test_order_vendor_delivery_admin_and_chart_helpers_use_real_rows_without_writes():
    db = make_db()
    active = get_active_purchase_orders_summary(db)
    assert active[0]["vendor_name"] == "Acme Supplies"
    assert active[0]["deadline_indicator"] == "Due Soon"
    performance = get_vendor_performance_dashboard(db)
    assert performance["best_performing_vendors"][0]["reliability_score"] == 82.0
    assert get_delivery_status_dashboard(db)["pending_shipments"] == 1
    vendor = get_vendor_dashboard_summary(db, 1)
    assert vendor["active_purchase_orders"] == 1
    assert vendor["payment_status"] == {"Pending": 1}
    assert get_admin_dashboard_summary(db)["system_activity_count"] == 1
    charts = get_dashboard_chart_data(db)
    assert charts["procurement_category_distribution"] == [{"category": "Steel", "count": 1}]
    assert charts["reliability_distribution"] == [{"risk_level": "Low Risk", "count": 1}]


def test_module8_empty_database_returns_only_zero_or_empty_aggregates():
    db = Db({})
    assert get_procurement_dashboard_summary(db)["total_procurement_requests"] == 0
    assert get_active_purchase_orders_summary(db) == []
    assert get_vendor_performance_dashboard(db)["vendors"] == []
    assert get_dashboard_chart_data(db)["monthly_procurement_expenses"] == []
