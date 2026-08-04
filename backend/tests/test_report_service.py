from unittest.mock import MagicMock
from app.services import report_service
import pytest


class EmptyQuery:
    def filter(self, _condition):
        return self

    def count(self):
        return 0

    def all(self):
        return []

    def first(self):
        return None

    def limit(self, _n):
        return self


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
    assert result["report_type"] == "contract"
    assert result["format"] == "csv"
    assert result["rows"] == []
    assert result["metadata"]["row_count"] == 0
    assert result["metadata"]["status"] == "prepared"


def test_export_rejects_unsupported_report_types_and_formats():
    with pytest.raises(ValueError, match="Unsupported report type"):
        report_service.export_report_data(EmptyDb(), "unknown")
    with pytest.raises(ValueError, match="Unsupported export format"):
        report_service.export_report_data(EmptyDb(), "contract", "json")


def test_vendor_performance_and_procurement_report_generators():
    db = EmptyDb()
    perf_rows = report_service.generate_vendor_performance_report(db)
    assert perf_rows == []
    proc_summary = report_service.generate_procurement_summary_report(db)
    assert proc_summary == []


def test_executive_summary_report_generator():
    db = EmptyDb()
    exec_summary = report_service.generate_executive_summary_report(db)
    assert "total_registered_vendors" in exec_summary
    assert "total_procurement_expenditure" in exec_summary
    assert "compliance_percentage" in exec_summary


def test_render_excel_csv_and_pdf_report_helpers():
    rows = [{"vendor_name": "ABC Steel", "score": 95.0}]
    csv_str = report_service.render_excel_csv_report(rows)
    assert "vendor_name,score" in csv_str
    assert "ABC Steel,95.0" in csv_str

    pdf_bytes = report_service.render_pdf_report("Vendor Performance", rows)
    assert isinstance(pdf_bytes, bytes)
    assert b"Vendor Reliability Intelligence Platform" in pdf_bytes
