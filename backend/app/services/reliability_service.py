from backend.app.utils.constants import RISK_LOW, RISK_MEDIUM, RISK_HIGH


def calculate_reliability_score(
    on_time_delivery_rate: float,
    quality_rating: float,
    response_score: float,
    contract_compliance: float,
    issue_resolution_score: float
) -> float:
    """
    Calculate vendor reliability score out of 100.

    Formula:
    - On-time delivery: 30%
    - Product quality: 25%
    - Communication response: 15%
    - Contract compliance: 20%
    - Issue resolution: 10%
    """
    score = (
        on_time_delivery_rate * 0.30 +
        quality_rating * 0.25 +
        response_score * 0.15 +
        contract_compliance * 0.20 +
        issue_resolution_score * 0.10
    )

    return round(score, 2)


def get_risk_level(score: float) -> str:
    """
    Classify vendor risk level based on reliability score.
    """
    if score >= 80:
        return RISK_LOW
    if score >= 50:
        return RISK_MEDIUM

    return RISK_HIGH


def generate_vendor_recommendation(score: float) -> str:
    """
    Generate procurement recommendation based on vendor reliability.
    """
    if score >= 80:
        return "Recommended vendor for procurement"
    if score >= 50:
        return "Use with caution and monitor performance"

    return "High risk vendor, avoid for critical procurement"