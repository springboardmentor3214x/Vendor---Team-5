"""Contract checks for Pranjali-owned Module 7–10 route registration and JWT gates."""

from fastapi.testclient import TestClient

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


def test_procurement_write_routes_require_jwt() -> None:
    for method, path in (("post", "/procurement/procurement-requests"), ("patch", "/procurement/purchase-orders/1/deliver"),
                         ("post", "/procurement/invoices"), ("patch", "/procurement/invoices/1/payment-status")):
        response = getattr(client, method)(path)
        assert response.status_code == 401, (path, response.status_code, response.text)
