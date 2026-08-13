from unittest.mock import MagicMock
from datetime import date
import pytest

from app.services import dashboard_service


def test_get_procurement_manager_dashboard_summary():
    db = MagicMock()
    db.query().all.return_value = []
    db.query().limit().all.return_value = []

    res = dashboard_service.get_procurement_manager_dashboard_summary(db=db)

    assert "procurement_summary" in res
    assert "delivery_summary" in res
    assert "requests_by_department" in res
    assert "top_vendors" in res
    assert res["procurement_summary"]["total_requests"] == 0
    assert res["delivery_summary"] == {
        "on_time_deliveries": 0,
        "delayed_deliveries": 0,
        "delivered_orders": 0,
        "pending_shipments": 0,
        "completed_deliveries": 0,
    }
    assert res["requests_by_department"] == {}


def test_get_personalized_vendor_dashboard():
    db = MagicMock()
    mock_vendor = MagicMock()
    mock_vendor.id = 1
    mock_vendor.company_name = "Sample Vendor"
    mock_vendor.reliability_score = 4.5
    db.query().filter().first.return_value = mock_vendor
    db.query().filter().all.return_value = []
    db.query().filter().count.return_value = 0

    res = dashboard_service.get_personalized_vendor_dashboard(db=db, vendor_id=1)

    assert res["vendor_id"] == 1
    assert res["company_name"] == "Sample Vendor"
    assert "reliability_score" in res


def test_get_admin_dashboard_summary():
    db = MagicMock()
    db.query().count.return_value = 5
    db.query().filter().count.return_value = 3
    db.query().all.return_value = []

    res = dashboard_service.get_admin_dashboard_summary(db=db)

    assert res["total_users"] == 5
    assert res["approved_vendors"] == 3
    assert "total_contract_value" in res


def test_get_procurement_cost_analysis():
    db = MagicMock()
    db.query().all.return_value = []

    res = dashboard_service.get_procurement_cost_analysis(db=db)

    assert "spending_by_department" in res
    assert "spending_by_category" in res
    assert "monthly_spending_trend" in res
    assert res["total_expenses"] == 0


def test_get_chart_datasets_summary():
    db = MagicMock()
    db.query().all.return_value = []

    res = dashboard_service.get_chart_datasets_summary(db=db)

    assert "monthly_expenses_chart" in res
    assert "vendor_performance_trend_chart" in res
    assert "category_distribution_chart" in res
    assert "contract_status_chart" in res

    assert res["monthly_expenses_chart"]["chart_type"] == "bar"
    assert res["vendor_performance_trend_chart"]["chart_type"] == "line"
    assert res["category_distribution_chart"]["chart_type"] == "pie"
    assert res["contract_status_chart"]["chart_type"] == "doughnut"


def test_dashboard_uses_vendor_reliability_score_field_not_removed_overall_score(monkeypatch):
    vendor = type("Vendor", (), {"id": 3, "company_name": "Real Vendor", "reliability_score": 0})()
    score = type("Score", (), {"vendor_id": 3, "reliability_score": 88.0})()

    class Query:
        def __init__(self, model): self.model = model
        def all(self): return [vendor] if self.model.__name__ == "Vendor" else []
        def limit(self, _): return self
        def filter(self, *_): return self
        def first(self): return score if self.model.__name__ == "VendorReliabilityScore" else None
    class Db:
        def query(self, model): return Query(model)
    result = dashboard_service.get_procurement_manager_dashboard_summary(Db())
    assert result["top_vendors"][0]["reliability_score"] == 88.0


def test_performance_trend_aggregation_uses_communication_score_not_response_minutes(monkeypatch):
    trend = type("Trend", (), {"vendor_id": 3, "year": 2026, "month": 8, "id": 1, "delivery_score": 90,
        "quality_score": 85, "communication_score": 80, "reliability_score": 84})()
    monkeypatch.setattr(dashboard_service, "_rows", lambda _db, model: [trend] if model.__name__ == "PerformanceTrend" else [])
    data = dashboard_service.get_performance_trend_aggregation(object(), 3)
    assert data["labels"] == ["2026-08"]
    assert next(row for row in data["datasets"] if row["label"] == "Communication")["data"] == [80]
