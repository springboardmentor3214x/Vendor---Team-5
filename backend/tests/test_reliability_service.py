from app.services.reliability_service import (
    calculate_reliability_score,
    get_risk_level,
    generate_vendor_recommendation,
    analyze_reliability_trend,
    calculate_average_reliability_score,
    calculate_vendor_reliability_score,
    classify_procurement_risk,
    compare_vendor_reliability,
    count_vendors_by_risk,
    filter_recommended_vendors,
    generate_procurement_recommendation,
    rank_vendors_by_reliability,
    recalculate_vendor_reliability,
    recalculate_supplier_rankings,
    should_warn_for_high_risk_vendor,
)
import pytest


def test_reliability_score_calculation():
    score = calculate_reliability_score(
        on_time_delivery_rate=90,
        quality_rating=85,
        response_score=80,
        contract_compliance=95,
        issue_resolution_score=75
    )

    assert score == 86.75


def test_low_risk_level():
    assert get_risk_level(85) == "Low"


def test_medium_risk_level():
    assert get_risk_level(60) == "Medium"


def test_high_risk_level():
    assert get_risk_level(40) == "High"


def test_recommendation_for_good_vendor():
    assert generate_vendor_recommendation(85) == "Recommended vendor for procurement"


def test_vendor_reliability_score_calculation_uses_all_six_factors():
    assert calculate_vendor_reliability_score(90, 80, 70, 60, 90, 80) == 80.5


def test_procurement_history_score_is_included_in_calculation():
    assert calculate_vendor_reliability_score(procurement_history_score=70) == 70


def test_missing_component_is_excluded_not_defaulted_to_100():
    assert calculate_vendor_reliability_score(delivery_score=80) == 80


def test_reliability_score_renormalizes_available_weights():
    assert calculate_vendor_reliability_score(delivery_score=80, quality_score=90) == 84.55


def test_reliability_score_returns_zero_when_all_components_are_missing():
    assert calculate_vendor_reliability_score() == 0


class _Query:
    def __init__(self, value):
        self.value = value

    def filter(self, *_args):
        return self

    def first(self):
        return self.value

    def all(self):
        return self.value if isinstance(self.value, list) else []


class _Session:
    def __init__(self, vendor=None, reliability=None, vendors=None, rows=None):
        self.vendor = vendor
        self.reliability = reliability
        self.vendors = vendors
        self.rows = rows or {}
        self.commits = 0
        self.refreshed = []
        self.added = []

    def query(self, model):
        from app.models.reliability import VendorReliability
        from app.models.vendor import Vendor

        if model is VendorReliability:
            return _Query(self.reliability)
        if model is Vendor:
            return _Query(self.vendors if self.vendors is not None else self.vendor)
        return _Query(self.rows.get(model, []))

    def commit(self):
        self.commits += 1

    def add(self, value):
        self.added.append(value)
        self.reliability = value

    def refresh(self, value):
        self.refreshed.append(value)


def test_recalculate_vendor_reliability_uses_real_model_shaped_records_and_persists_derivatives():
    from datetime import timedelta
    from app.models.certification import Certification
    from app.models.communication_log import CommunicationLog
    from app.models.compliance import ComplianceRecord
    from app.models.contract import Contract
    from app.models.delivery_performance import DeliveryPerformance
    from app.models.product_quality_evaluation import ProductQualityEvaluation
    from app.models.procurement_request import ProcurementRequest
    from app.models.purchase_order import PurchaseOrder
    from app.models.service_rating import ServiceRating
    from app.models.vendor_document import VendorDocument
    from app.models.reliability import PerformanceTrend, ProcurementRecommendation

    vendor = type("Vendor", (), {"id": 7, "reliability_score": 0.0})()
    reliability = type("Reliability", (), {
        "id": 1,
        "vendor_id": 7,
        "delivery_score": 0.0, "quality_score": 0.0, "communication_score": 0.0,
        "compliance_score": 0.0, "issue_resolution_score": 0.0,
        "updated_at": None,
    })()
    rows = {
        PurchaseOrder: [type("PO", (), {"id": 10, "vendor_id": 7, "po_status": "Delivered"})()],
        ProcurementRequest: [type("Request", (), {"vendor_id": 7, "approval_status": "Rejected"})()],
        DeliveryPerformance: [type("Delivery", (), {"vendor_id": 7, "delay_days": 2, "delivery_status": "Delayed Delivery"})()],
        ProductQualityEvaluation: [type("Quality", (), {"vendor_id": 7, "overall_quality_rating": 4.0})()],
        CommunicationLog: [type("Communication", (), {"vendor_id": 7, "response_duration_minutes": 180, "communication_status": "Responded"})()],
        ServiceRating: [type("Service", (), {"vendor_id": 7, "communication_effectiveness": None, "issue_resolution": 3.0})()],
        Contract: [type("Contract", (), {"vendor_id": 7, "compliance_verified": True})()],
        ComplianceRecord: [type("Compliance", (), {"vendor_id": 7, "status": "Compliant"})()],
        Certification: [type("Certification", (), {"vendor_id": 7, "expiry_date": __import__("datetime").datetime.utcnow() + timedelta(days=1)})()],
        VendorDocument: [type("Document", (), {"vendor_id": 7})()],
        PerformanceTrend: [], ProcurementRecommendation: [],
    }
    db = _Session(vendor, reliability, rows=rows)

    result = recalculate_vendor_reliability(7, db)

    assert result is reliability
    assert not isinstance(result, dict)
    for field in (
        "id", "vendor_id", "delivery_score", "quality_score",
        "communication_score", "compliance_score", "issue_resolution_score",
        "reliability_score", "risk_level", "updated_at",
    ):
        assert hasattr(result, field)
    assert result.delivery_score == 80.0
    assert result.quality_score == 80.0
    assert result.communication_score == 80.0
    assert result.issue_resolution_score == 60.0
    assert result.compliance_score == 100.0
    # PO success (100) and rejected request (0) yield procurement history 50,
    # proving it is independent of the 100 compliance score.
    assert result.reliability_score == 77.0
    assert result.risk_level == "Medium Risk"
    assert any(isinstance(row, PerformanceTrend) for row in db.added)
    assert any(isinstance(row, ProcurementRecommendation) for row in db.added)
    assert db.commits == 1


def test_recalculate_vendor_reliability_does_not_default_missing_data_to_100():
    db = _Session(vendor=type("Vendor", (), {"id": 8, "reliability_score": 0.0})())

    result = recalculate_vendor_reliability(8, db)
    assert result.reliability_score == 0
    assert result.risk_level == "High Risk"
    assert db.added[0] is result


def test_reliability_write_trigger_helpers_delegate_to_the_recalculation(monkeypatch):
    import app.services.reliability_service as service

    calls = []
    monkeypatch.setattr(service, "recalculate_vendor_reliability", lambda vendor_id, db: calls.append((vendor_id, db)) or "updated")
    monkeypatch.setattr(service, "recalculate_supplier_rankings", lambda db: calls.append(("rankings", db)) or [])
    db = object()
    assert service.refresh_vendor_reliability_after_performance_write(3, db) == "updated"
    assert service.refresh_vendor_reliability_after_procurement_update(3, db) == "updated"
    assert service.refresh_vendor_reliability_after_compliance_update(3, db) == "updated"
    assert calls == [(3, db), ("rankings", db), (3, db), (3, db)]


def test_recalculate_supplier_rankings_accepts_db_and_handles_no_vendors():
    assert recalculate_supplier_rankings(_Session(vendors=[])) == []


def test_recalculate_supplier_rankings_uses_reliability_rows_not_performance_ranking():
    high = type("Reliability", (), {
        "vendor_id": 2, "reliability_score": 92.0, "risk_level": "Low Risk",
    })()
    low = type("Reliability", (), {
        "vendor_id": 1, "reliability_score": 67.0, "risk_level": "High Risk",
    })()
    db = _Session(reliability=[low, high])

    rankings = recalculate_supplier_rankings(db)

    assert [row["vendor_id"] for row in rankings] == [2, 1]
    assert [row["reliability_score"] for row in rankings] == [92.0, 67.0]
    assert [row["rank_position"] for row in rankings] == [1, 2]


@pytest.mark.parametrize(("score", "expected"), [(90, "Low Risk"), (70, "Medium Risk"), (69, "High Risk")])
def test_procurement_risk_classification(score, expected):
    assert classify_procurement_risk(score) == expected


def test_procurement_recommendations_and_high_priority_warning():
    assert generate_procurement_recommendation(95, "Low Risk") == "Recommended for procurement"
    assert generate_procurement_recommendation(75, "Medium Risk") == "Recommended with monitoring"
    assert generate_procurement_recommendation(40, "High Risk", True) == (
        "High risk vendor. Additional approval required for high-priority procurement."
    )


def test_vendor_ranking_is_descending_and_adds_positions():
    ranked = rank_vendors_by_reliability([
        {"vendor_id": 1, "vendor_name": "ABC", "reliability_score": 78},
        {"vendor_id": 2, "vendor_name": "XYZ", "reliability_score": 92},
    ])
    assert [vendor["vendor_id"] for vendor in ranked] == [2, 1]
    assert [vendor["rank_position"] for vendor in ranked] == [1, 2]


@pytest.mark.parametrize(("history", "expected"), [
    ([70, 75], "Improving"), ([80, 75], "Declining"), ([80, 82], "Stable"), ([80], "Insufficient Data"),
])
def test_reliability_trends(history, expected):
    assert analyze_reliability_trend(history) == expected


def test_average_reliability_score_and_empty_list():
    assert calculate_average_reliability_score([80, 90, 85]) == 85
    assert calculate_average_reliability_score([]) == 0


def test_count_vendors_by_risk():
    counts = count_vendors_by_risk([
        {"reliability_score": 95}, {"reliability_score": 70}, {"reliability_score": 30},
    ])
    assert counts == {"low_risk_count": 1, "medium_risk_count": 1, "high_risk_count": 1}


def test_high_risk_warning_and_recommended_vendor_filter():
    assert should_warn_for_high_risk_vendor("High Risk") is True
    vendors = [
        {"vendor_id": 1, "reliability_score": 65},
        {"vendor_id": 2, "reliability_score": 75},
        {"vendor_id": 3, "reliability_score": 95},
    ]
    assert [vendor["vendor_id"] for vendor in filter_recommended_vendors(vendors)] == [3, 2]


def test_vendor_comparison_and_tie():
    vendor_a = {"vendor_id": 1, "vendor_name": "ABC", "reliability_score": 80}
    vendor_b = {"vendor_id": 2, "vendor_name": "XYZ", "reliability_score": 90}
    assert compare_vendor_reliability(vendor_a, vendor_b) == {
        "better_vendor_id": 2, "better_vendor_name": "XYZ", "score_difference": 10,
    }
    vendor_b["reliability_score"] = 80
    assert compare_vendor_reliability(vendor_a, vendor_b) == {
        "better_vendor_id": None, "better_vendor_name": "Tie", "score_difference": 0,
    }


def test_invalid_score_raises_value_error():
    with pytest.raises(ValueError):
        calculate_vendor_reliability_score(101, 80, 70, 60, 90, 80)


def test_score_below_zero_raises_value_error():
    with pytest.raises(ValueError):
        calculate_vendor_reliability_score(delivery_score=-1)
