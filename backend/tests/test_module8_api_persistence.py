"""API-layer regression coverage for Module 8 persistence and scoping."""

from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.auth import get_current_user
from app.api.procurement import create_purchase_order
from app.core.database import get_db
from app.main import app
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.vendor import Vendor
from app.schemas.procurement import PurchaseOrderCreate


class _Query:
    def __init__(self, first_value=None, count_value=0):
        self.first_value = first_value
        self.count_value = count_value

    def filter(self, *_predicates):
        return self

    def first(self):
        return self.first_value

    def count(self):
        return self.count_value


class _PurchaseOrderDb:
    def __init__(self):
        self.request = SimpleNamespace(id=1, vendor_id=2, approval_status="Approved", project_name="Alpha Expansion")
        self.added = []

    def query(self, model):
        if model is ProcurementRequest:
            return _Query(self.request)
        if model is PurchaseOrder:
            return _Query(None, 0)
        return _Query(None)

    def add(self, item):
        self.added.append(item)

    def commit(self):
        pass

    def refresh(self, item):
        if isinstance(item, PurchaseOrder):
            item.id = 1


def test_purchase_order_inherits_project_and_persists_assigned_manager():
    db = _PurchaseOrderDb()
    payload = PurchaseOrderCreate.model_validate({
        "procurementRequestId": 1,
        "quantityOrdered": 2,
        "unitPrice": 50,
        "expectedDeliveryDate": "2026-12-01T00:00:00",
    })
    current_user = SimpleNamespace(id=99, role="Procurement Manager", email="manager@example.test")

    purchase_order = create_purchase_order(payload, current_user, db)

    assert purchase_order.assigned_procurement_manager_id == 99
    assert purchase_order.project_name == "Alpha Expansion"
    assert purchase_order.created_by == 99


class _NoLinkedVendorDb:
    def query(self, _model):
        return _Query(None)


def test_vendor_dashboard_does_not_fall_back_to_an_unrelated_vendor():
    vendor_user = SimpleNamespace(id=7, email="no-vendor@example.test", role="Vendor", is_active=True)
    app.dependency_overrides[get_current_user] = lambda: vendor_user
    app.dependency_overrides[get_db] = lambda: _NoLinkedVendorDb()
    try:
        with TestClient(app) as client:
            response = client.get("/dashboard/vendor")
        assert response.status_code == 404, response.text
        assert response.json()["detail"] == "No vendor record is linked to this user"
    finally:
        app.dependency_overrides.clear()
