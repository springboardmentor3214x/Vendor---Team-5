from backend.app.services.reliability_service import (
    calculate_reliability_score,
    get_risk_level,
    generate_vendor_recommendation
)


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