from app.services import report_service
import pytest


class EmptyQuery:
    def filter(self, _condition):
        return self

    def all(self):
        return []


class EmptyDb:
    def query(self, _model):
        return EmptyQuery()


def test_reports_return_empty_real_data_sets_not_fake_rows():
    db = EmptyDb()
    assert report_service.generate_contract_report(db) == []
    assert report_service.generate_compliance_report(db) == []
    assert report_service.generate_vendor_document_report(db) == []
    assert report_service.generate_notification_report(db, {"user_id": 3}) == []


def test_export_prepares_data_without_writing_files():
    result = report_service.export_report_data(EmptyDb(), "contract", "csv")
    assert result == {
        "report_type": "contract", "format": "csv", "rows": [],
        "metadata": {"row_count": 0, "status": "prepared"},
    }


def test_export_rejects_unsupported_report_types_and_formats():
    with pytest.raises(ValueError, match="Unsupported report type"):
        report_service.export_report_data(EmptyDb(), "unknown")
    with pytest.raises(ValueError, match="Unsupported export format"):
        report_service.export_report_data(EmptyDb(), "contract", "json")


def test_contract_report_uses_database_record_values():
    record = type("ContractRecord", (), {
        "id": 1, "vendor_id": 4, "contract_number": "C-1", "contract_title": "Supply",
        "status": "Active", "start_date": None, "end_date": None, "contract_value": 100.0,
    })()

    class Db:
        def query(self, _model):
            return EmptyQueryWithRows([record])

    assert report_service.generate_contract_report(Db()) == [{
        "id": 1, "vendor_id": 4, "contract_number": "C-1", "contract_title": "Supply",
        "status": "Active", "start_date": None, "end_date": None, "contract_value": 100.0,
    }]


class EmptyQueryWithRows(EmptyQuery):
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


def test_vendor_performance_report_uses_real_performance_and_reliability_rows():
    from app.models.performance import PerformanceRecord
    from app.models.reliability import VendorReliability

    performance = type("Performance", (), {
        "id": 1, "vendor_id": 7, "total_completed_orders": 3, "on_time_delivery_rate": 80.0,
        "delayed_delivery_count": 1, "average_quality_score": 85.0, "average_response_time": 90.0,
        "average_service_rating_score": 80.0, "overall_performance_score": 82.0,
        "performance_status": "Excellent", "evaluation_date": None,
    })()
    reliability = type("Reliability", (), {"vendor_id": 7, "reliability_score": 79.0, "risk_level": "Medium Risk"})()

    class Db:
        def query(self, model):
            return EmptyQueryWithRows([performance] if model is PerformanceRecord else [reliability])

    row = report_service.generate_vendor_performance_report(Db())[0]
    assert row["vendor_id"] == 7
    assert row["overall_performance_score"] == 82.0
    assert row["reliability_score"] == 79.0


def test_procurement_summary_report_uses_real_request_and_purchase_order_rows():
    from app.models.procurement_request import ProcurementRequest
    from app.models.purchase_order import PurchaseOrder

    request = type("Request", (), {
        "id": 4, "request_number": "PR-4", "title": "Steel", "department": "Ops", "vendor_id": 7,
        "quantity": 2, "estimated_budget": 100.0, "priority": "High", "approval_status": "Approved",
        "request_date": None, "approved_date": None,
    })()
    order = type("Order", (), {
        "id": 8, "procurement_request_id": 4, "po_number": "PO-8", "po_status": "Delivered",
        "total_cost": 98.0, "expected_delivery_date": None, "actual_delivery_date": None,
    })()

    class Db:
        def query(self, model):
            return EmptyQueryWithRows([request] if model is ProcurementRequest else [order])

    row = report_service.generate_procurement_summary_report(Db())[0]
    assert row["procurement_request_id"] == 4
    assert row["purchase_order_id"] == 8
    assert row["po_status"] == "Delivered"
