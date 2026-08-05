"""Contract checks for Pranjali-owned Module 7–10 route registration and JWT gates."""

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.auth import get_current_user
from app.main import app


client = TestClient(app)


def test_module7_to_10_routes_are_registered() -> None:
    paths = app.openapi()["paths"]
    required = {
        "/communications/", "/communications/{communication_id}/read", "/communications/files",
        "/discussions/", "/discussions/{discussion_id}", "/activity-logs/",
        "/dashboard/procurement-manager", "/dashboard/vendor", "/dashboard/admin", "/dashboard/charts",
        "/notifications/summary", "/notifications/read-all", "/notifications/{notification_id}",
        "/reports/{report_key}/preview", "/reports/{report_key}/charts", "/reports/{report_key}/export",
        "/reports/purchase-orders", "/reports/executive-summary",
    }
    assert required <= set(paths)


def test_module7_to_10_read_routes_require_jwt() -> None:
    for path in ("/communications/", "/discussions/", "/activity-logs/", "/dashboard/procurement-manager",
                 "/notifications/summary", "/reports/purchase-orders"):
        response = client.get(path)
        assert response.status_code == 401, (path, response.status_code, response.text)


def test_communication_file_route_is_not_captured_by_dynamic_message_route() -> None:
    """Regression: `/communications/files` must reach its JWT gate, not `/{id}` validation."""
    response = client.post("/communications/files")
    assert response.status_code == 401, response.text
    assert response.status_code != 422


def test_communication_upload_policy_is_explicit() -> None:
    from app.api.communications import COMMUNICATION_ALLOWED_EXTENSIONS, COMMUNICATION_MAX_UPLOAD_BYTES

    assert {"pdf", "xlsx", "docx", "png", "zip"} <= COMMUNICATION_ALLOWED_EXTENSIONS
    assert COMMUNICATION_MAX_UPLOAD_BYTES == 10 * 1024 * 1024


def test_all_procurement_write_routes_require_jwt() -> None:
    routes = (
        ("post", "/procurement/procurement-requests"),
        ("patch", "/procurement/procurement-requests/1"),
        ("delete", "/procurement/procurement-requests/1"),
        ("patch", "/procurement/procurement-requests/1/approve"),
        ("patch", "/procurement/procurement-requests/1/reject"),
        ("patch", "/procurement/procurement-requests/1/send-back"),
        ("patch", "/procurement/procurement-requests/1/cancel"),
        ("patch", "/procurement/procurement-requests/1/assign-vendor"),
        ("post", "/procurement/purchase-orders"),
        ("patch", "/procurement/purchase-orders/1/status"),
        ("patch", "/procurement/purchase-orders/1/issue"),
        ("patch", "/procurement/purchase-orders/1/deliver"),
        ("patch", "/procurement/purchase-orders/1/cancel"),
        ("post", "/procurement/purchase-orders/1/completion-check"),
        ("patch", "/procurement/order-tracking/1"),
        ("post", "/procurement/invoices"),
        ("patch", "/procurement/invoices/1/verify"),
        ("patch", "/procurement/invoices/1/reject"),
        ("patch", "/procurement/invoices/1/payment-status"),
    )
    for method, path in routes:
        response = getattr(client, method)(path)
        assert response.status_code == 401, (path, response.status_code, response.text)


def test_procurement_approval_writes_reject_non_approver_before_request_validation() -> None:
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=99, role="Finance Officer")
    try:
        response = client.patch("/procurement/procurement-requests/1/approve")
        assert response.status_code == 403, response.text
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_report_discovery_advertises_all_generic_export_formats() -> None:
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=1, role="Administrator")
    try:
        response = client.get("/reports/")
        assert response.status_code == 200, response.text
        assert set(response.json()["items"][0]["formats"]) == {"json", "csv", "xlsx", "pdf"}
    finally:
        app.dependency_overrides.pop(get_current_user, None)
