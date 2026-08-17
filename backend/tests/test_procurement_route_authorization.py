"""Regression coverage for action-level procurement role enforcement."""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.auth import get_current_user
from app.core.database import get_db
from app.main import app


class _UnusedDb:
    """Role checks must reject before a database query is needed."""


@pytest.fixture
def client_for_role():
    def build(role: str) -> TestClient:
        user = SimpleNamespace(id=42, email=f"{role.lower().replace(' ', '.')}@example.test", role=role, is_active=True)
        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[get_db] = lambda: _UnusedDb()
        return TestClient(app)

    yield build
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("role", "method", "path", "payload"),
    [
        ("Vendor", "patch", "/procurement/procurement-requests/1/approve", {"remarks": "not allowed"}),
        ("Supply Chain Manager", "post", "/procurement/purchase-orders", {
            "procurementRequestId": 1, "quantityOrdered": 1, "unitPrice": 10,
            "expectedDeliveryDate": "2026-12-01T00:00:00",
        }),
        ("Finance Officer", "patch", "/procurement/procurement-requests/1/assign-vendor", {"vendorId": 2}),
        ("Procurement Manager", "post", "/procurement/invoices", {
            "purchaseOrderId": 1, "invoiceNumber": "INV-TEST-1", "invoiceAmount": 10,
            "invoiceDate": "2026-12-01T00:00:00",
        }),
        ("Vendor", "patch", "/procurement/invoices/1/payment-status", {"paymentStatus": "Approved"}),
    ],
)
def test_wrong_procurement_role_is_rejected_before_mutation(client_for_role, role, method, path, payload):
    with client_for_role(role) as client:
        response = getattr(client, method)(path, json=payload)
    assert response.status_code == 403, response.text


def test_unauthenticated_procurement_mutation_is_rejected():
    with TestClient(app) as client:
        response = client.patch("/procurement/procurement-requests/1/approve", json={"remarks": "x"})
    assert response.status_code == 401, response.text
