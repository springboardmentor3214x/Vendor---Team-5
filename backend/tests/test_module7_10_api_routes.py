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
