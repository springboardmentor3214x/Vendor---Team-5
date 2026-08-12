"""Regression coverage for the Module 10 report API contract."""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api import reports as reports_api
from app.api.auth import get_current_user
from app.core.database import get_db
from app.main import app


class _UnusedDb:
    """The report generators are replaced in these API-contract tests."""


@pytest.fixture
def report_client():
    user = SimpleNamespace(id=1, email="auditor@example.test", role="Auditor", is_active=True)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: _UnusedDb()
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


def test_preview_and_export_share_validated_filter_and_sort_contract(report_client, monkeypatch):
    calls = []

    def performance_rows(_db, filters=None):
        calls.append(filters)
        return [
            {"vendor_id": 1, "risk_level": "Low", "overall_performance_score": 72},
            {"vendor_id": 2, "risk_level": "Low", "overall_performance_score": 93},
            {"vendor_id": 3, "risk_level": "High", "overall_performance_score": 99},
        ]

    monkeypatch.setitem(reports_api._REPORT_GENERATORS, "vendor-performance", performance_rows)
    query = "reliabilityLevel=Low&sortBy=overall_performance_score&sortOrder=desc"

    preview = report_client.get(f"/reports/vendor-performance/preview?{query}")
    export = report_client.get(f"/reports/vendor-performance/export?format=csv&{query}")

    assert preview.status_code == 200, preview.text
    assert [row["vendor_id"] for row in preview.json()["rows"]] == [2, 1]
    assert export.status_code == 200, export.text
    assert "2,Low,93" in export.text
    assert "3,High,99" not in export.text
    assert calls == [None, None]


def test_preview_rejects_unknown_sort_field_before_returning_rows(report_client, monkeypatch):
    monkeypatch.setitem(reports_api._REPORT_GENERATORS, "contracts", lambda _db, _filters=None: [])

    response = report_client.get("/reports/contracts/preview?sortBy=notARealField")

    assert response.status_code == 400
    assert response.json()["detail"] == "sortBy is not supported for this report type"


def test_contract_expiry_window_filters_persisted_contract_report_rows(report_client, monkeypatch):
    monkeypatch.setattr(
        reports_api.report_service,
        "generate_contract_report",
        lambda _db, _filters=None: [
            {"contract_number": "CT-15", "days_to_expiry": 15},
            {"contract_number": "CT-60", "days_to_expiry": 60},
            {"contract_number": "CT-120", "days_to_expiry": 120},
            {"contract_number": "CT-OLD", "days_to_expiry": -1},
        ],
    )

    response = report_client.get("/reports/contracts/expiring?window=30")

    assert response.status_code == 200, response.text
    assert response.json()["window_days"] == 30
    assert [row["contract_number"] for row in response.json()["rows"]] == ["CT-15"]


def test_report_discovery_advertises_excel_when_generic_export_supports_it(report_client):
    response = report_client.get("/reports/")

    assert response.status_code == 200, response.text
    for item in response.json()["items"]:
        assert "excel" in item["formats"]


def test_report_chart_endpoint_uses_the_same_filtered_rows(report_client, monkeypatch):
    monkeypatch.setitem(
        reports_api._REPORT_GENERATORS,
        "vendor-performance",
        lambda _db, _filters=None: [
            {"vendor_id": 1, "risk_level": "Low", "overall_performance_score": 72},
            {"vendor_id": 2, "risk_level": "High", "overall_performance_score": 91},
        ],
    )

    response = report_client.get("/reports/vendor-performance/charts?reliabilityLevel=Low")

    assert response.status_code == 200, response.text
    assert response.json()["chart_data"]["labels"] == ["1"]
    assert response.json()["chart_data"]["datasets"][0]["data"] == [72.0]


def test_report_chart_endpoint_returns_explicit_empty_data_when_not_meaningful(report_client, monkeypatch):
    monkeypatch.setitem(reports_api._REPORT_GENERATORS, "executive-summary", lambda _db, _filters=None: {"total": 1})

    response = report_client.get("/reports/executive-summary/charts")

    assert response.status_code == 200, response.text
    assert response.json()["chart_data"]["chart_type"] == "none"
    assert "reason" in response.json()
