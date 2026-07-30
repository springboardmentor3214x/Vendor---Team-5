from app.services import report_service


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
