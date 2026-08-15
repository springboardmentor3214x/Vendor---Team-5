from unittest.mock import MagicMock
from app.services import report_service
import pytest
from types import SimpleNamespace
from app.models.compliance import ComplianceRecord


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
    with pytest.raises(ValueError, match="reliability_level"):
        report_service.export_report_data(EmptyDb(), "contract", filters={"reliability_level": "Low"})


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
    assert exec_summary["compliance_percentage"] is None


def test_executive_summary_calculates_compliance_percentage_from_records(monkeypatch):
    records = [SimpleNamespace(status="Compliant"), SimpleNamespace(status="Pending Verification")]
    original_filtered = report_service._filtered

    def filtered(db, model, filters=None):
        return records if model is ComplianceRecord else original_filtered(db, model, filters)

    monkeypatch.setattr(report_service, "_filtered", filtered)
    assert report_service.generate_executive_summary_report(EmptyDb())["compliance_percentage"] == 50.0


def test_export_uses_report_specific_chart_fields(monkeypatch):
    monkeypatch.setattr(
        report_service,
        "generate_compliance_report",
        lambda _db, _filters=None: [{"status": "Compliant", "id": 7}],
    )
    chart = report_service.export_report_data(EmptyDb(), "compliance")["chart_data"]
    assert chart["labels"] == ["Compliant"]
    assert chart["datasets"][0]["label"] == "Id"


def test_render_excel_csv_and_pdf_report_helpers():
    rows = [{"vendor_name": "ABC Steel", "score": 95.0}]
    csv_str = report_service.render_excel_csv_report(rows)
    assert "vendor_name,score" in csv_str
    assert "ABC Steel,95.0" in csv_str

    pdf_bytes = report_service.render_pdf_report("Vendor Performance", rows)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")

    xlsx_bytes = report_service.render_excel_report(rows)
    assert xlsx_bytes.startswith(b"PK")
