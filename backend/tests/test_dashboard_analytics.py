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
