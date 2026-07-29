from datetime import date, timedelta
from types import SimpleNamespace

from app.services.dashboard_service import get_contract_dashboard_summary, get_module6_dashboard_summary


class EmptyQuery:
    def all(self):
        return []

    def count(self):
        return 0


class EmptyDb:
    def query(self, _model):
        return EmptyQuery()


def test_module6_dashboard_handles_an_empty_database():
    assert get_module6_dashboard_summary(EmptyDb(), user_id=1) == {
        "contracts": {"total_contracts": 0, "active_contracts": 0, "expired_contracts": 0, "expiring_soon_contracts": 0},
        "compliance": {"total_compliance_records": 0, "compliant_count": 0, "non_compliant_count": 0, "pending_count": 0, "expired_count": 0},
        "documents": {"total_documents": 0, "total_certifications": 0, "expired_certifications": 0, "expiring_soon_certifications": 0},
        "notifications": {"total_notifications": 0, "unread_notifications": 0},
    }


def test_contract_dashboard_aggregates_real_model_shaped_records():
    today = date.today()
    contracts = [
        SimpleNamespace(start_date=today - timedelta(days=10), end_date=today + timedelta(days=5)),
        SimpleNamespace(start_date=today - timedelta(days=10), end_date=today - timedelta(days=1)),
        SimpleNamespace(start_date=today + timedelta(days=2), end_date=today + timedelta(days=20)),
    ]

    class ContractDb:
        def query(self, _model):
            return SimpleNamespace(all=lambda: contracts)

    assert get_contract_dashboard_summary(ContractDb()) == {
        "total_contracts": 3, "active_contracts": 1, "expired_contracts": 1, "expiring_soon_contracts": 1,
    }
