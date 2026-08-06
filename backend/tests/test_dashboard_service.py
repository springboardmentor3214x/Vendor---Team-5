from datetime import date, timedelta
from types import SimpleNamespace

from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.user import User
from app.models.vendor import Vendor
from app.services.dashboard_service import (
    get_active_purchase_orders_summary,
    get_contract_dashboard_summary,
    get_module6_dashboard_summary,
    get_procurement_cost_analysis,
)


class EmptyQuery:
    def all(self):
        return []

    def count(self):
        return 0


class EmptyDb:
    def query(self, _model):
        return EmptyQuery()


def test_module6_dashboard_handles_an_empty_database():
    assert get_module6_dashboard_summary(EmptyDb(), user_id=1) == {
        "contracts": {"total_contracts": 0, "active_contracts": 0, "expired_contracts": 0, "expiring_soon_contracts": 0},
        "compliance": {"total_compliance_records": 0, "compliant_count": 0, "non_compliant_count": 0, "pending_count": 0, "expired_count": 0},
        "documents": {"total_documents": 0, "total_certifications": 0, "expired_certifications": 0, "expiring_soon_certifications": 0},
        "notifications": {"total_notifications": 0, "unread_notifications": 0},
    }


def test_module6_dashboard_handles_an_unavailable_database():
    assert get_module6_dashboard_summary(None, user_id=1) == {
        "contracts": {"total_contracts": 0, "active_contracts": 0, "expired_contracts": 0, "expiring_soon_contracts": 0},
        "compliance": {"total_compliance_records": 0, "compliant_count": 0, "non_compliant_count": 0, "pending_count": 0, "expired_count": 0},
        "documents": {"total_documents": 0, "total_certifications": 0, "expired_certifications": 0, "expiring_soon_certifications": 0},
        "notifications": {"total_notifications": 0, "unread_notifications": 0},
    }


def test_contract_dashboard_aggregates_real_model_shaped_records():
    today = date.today()
    contracts = [
        SimpleNamespace(start_date=today - timedelta(days=10), end_date=today + timedelta(days=5)),
        SimpleNamespace(start_date=today - timedelta(days=10), end_date=today - timedelta(days=1)),
        SimpleNamespace(start_date=today + timedelta(days=2), end_date=today + timedelta(days=20)),
    ]

    class ContractDb:
        def query(self, _model):
            return SimpleNamespace(all=lambda: contracts)

    assert get_contract_dashboard_summary(ContractDb()) == {
        "total_contracts": 3, "active_contracts": 1, "expired_contracts": 1, "expiring_soon_contracts": 1,
    }


def test_active_purchase_order_resolves_assigned_manager_and_preserves_existing_fields():
    today = date.today()
    request = SimpleNamespace(id=10, product_category="Equipment")
    order = SimpleNamespace(id=20, procurement_request_id=10, vendor_id=30, po_number="PO-001", po_status="Issued",
                            assigned_procurement_manager_id=40, total_cost=125.5, po_date=today,
                            expected_delivery_date=today + timedelta(days=3))
    manager = SimpleNamespace(id=40, full_name="Asha Manager")
    vendor = SimpleNamespace(id=30, company_name="Acme Supplies")

    class DashboardDb:
        def query(self, model):
            records = {
                ProcurementRequest: [request], PurchaseOrder: [order], Vendor: [vendor], User: [manager],
            }.get(model, [])
            return SimpleNamespace(all=lambda: records)

    active_order = get_active_purchase_orders_summary(DashboardDb())[0]
    assert active_order["assigned_procurement_manager"] == "Asha Manager"
    assert active_order["purchase_order_number"] == "PO-001"
    assert active_order["vendor_name"] == "Acme Supplies"
    assert active_order["procurement_category"] == "Equipment"
    assert active_order["status"] == "Issued"


def test_active_purchase_order_returns_none_when_no_manager_is_assigned():
    order = SimpleNamespace(id=20, procurement_request_id=10, po_status="Issued")

    class DashboardDb:
        def query(self, model):
            records = {ProcurementRequest: [SimpleNamespace(id=10)], PurchaseOrder: [order]}.get(model, [])
            return SimpleNamespace(all=lambda: records)

    assert get_active_purchase_orders_summary(DashboardDb())[0]["assigned_procurement_manager"] is None


def test_procurement_cost_analysis_groups_by_purchase_order_project_then_request_project():
    today = date.today()
    request = SimpleNamespace(id=10, project_name="Request project", product_category="Equipment", department="Operations")
    orders = [
        SimpleNamespace(id=20, procurement_request_id=10, vendor_id=30, project_name="Purchase order project", total_cost=100, po_date=today),
        SimpleNamespace(id=21, procurement_request_id=10, vendor_id=30, project_name=None, total_cost=25, po_date=today),
    ]

    class DashboardDb:
        def query(self, model):
            records = {ProcurementRequest: [request], PurchaseOrder: orders}.get(model, [])
            return SimpleNamespace(all=lambda: records)

    analysis = get_procurement_cost_analysis(DashboardDb())
    assert analysis["project_spending"] == [
        {"project": "Purchase order project", "total": 100.0},
        {"project": "Request project", "total": 25.0},
    ]
    assert {"spending_by_vendor", "spending_by_category", "monthly_expenses", "department_spending"} <= set(analysis)


def test_procurement_dashboard_service_returns_safe_empty_collections():
    db = EmptyDb()
    analysis = get_procurement_cost_analysis(db)
    assert get_active_purchase_orders_summary(db) == []
    assert analysis == {
        "spending_by_vendor": [], "spending_by_category": [], "monthly_expenses": [],
        "department_spending": [], "project_spending": [],
    }
