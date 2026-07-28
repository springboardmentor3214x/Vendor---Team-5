from app.utils.constants import RISK_LOW, RISK_MEDIUM, RISK_HIGH


LOW_RISK = "Low Risk"
MEDIUM_RISK = "Medium Risk"
HIGH_RISK = "High Risk"
TREND_IMPROVING = "Improving"
TREND_DECLINING = "Declining"
TREND_STABLE = "Stable"
TREND_INSUFFICIENT_DATA = "Insufficient Data"


def _validate_score(score: float) -> None:
    """Raise ValueError when a reliability component is outside 0--100."""
    if not 0 <= score <= 100:
        raise ValueError("Scores must be between 0 and 100.")


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
    # Preserve the legacy 20% contract weighting by representing it as the
    # Module 5 contract and procurement-history slots (10% each).
    return calculate_vendor_reliability_score(
        delivery_score=on_time_delivery_rate,
        quality_score=quality_rating,
        communication_score=response_score,
        issue_resolution_score=issue_resolution_score,
        procurement_history_score=contract_compliance,
        contract_compliance_score=contract_compliance,
    )


def get_risk_level(score: float) -> str:
    """
    Classify vendor risk level based on reliability score.
    """
    _validate_score(score)
    if score >= 80:
        return RISK_LOW
    if score >= 50:
        return RISK_MEDIUM

    return RISK_HIGH


def generate_vendor_recommendation(score: float) -> str:
    """
    Generate procurement recommendation based on vendor reliability.
    """
    _validate_score(score)
    if score >= 80:
        return "Recommended vendor for procurement"
    if score >= 50:
        return "Use with caution and monitor performance"

    return "High risk vendor, avoid for critical procurement"


def calculate_vendor_reliability_score(
    delivery_score: float | None = None,
    quality_score: float | None = None,
    communication_score: float | None = None,
    issue_resolution_score: float | None = None,
    procurement_history_score: float | None = None,
    contract_compliance_score: float | None = None,
) -> float:
    """Calculate the available Module 5 components as a score out of 100.

    Missing components are excluded and the remaining weights are normalized,
    so incomplete data never improves a vendor's score by defaulting to 100.
    """
    weighted_components = (
        (delivery_score, 0.30),
        (quality_score, 0.25),
        (communication_score, 0.15),
        (issue_resolution_score, 0.10),
        (procurement_history_score, 0.10),
        (contract_compliance_score, 0.10),
    )
    available_components = []
    for score, weight in weighted_components:
        if score is not None:
            _validate_score(score)
            available_components.append((score, weight))

    if not available_components:
        return 0

    weighted_score = sum(score * weight for score, weight in available_components)
    available_weight = sum(weight for _, weight in available_components)
    return round(weighted_score / available_weight, 2)


def classify_procurement_risk(reliability_score: float) -> str:
    """Classify reliability using the Module 5 procurement thresholds."""
    _validate_score(reliability_score)
    if reliability_score >= 90:
        return LOW_RISK
    if reliability_score >= 70:
        return MEDIUM_RISK
    return HIGH_RISK


def generate_procurement_recommendation(
    reliability_score: float, risk_level: str, is_high_priority: bool = False
) -> str:
    """Return a recommendation appropriate to the supplied procurement risk."""
    _validate_score(reliability_score)
    if risk_level == HIGH_RISK and is_high_priority:
        return "High risk vendor. Additional approval required for high-priority procurement."
    if risk_level == LOW_RISK:
        return "Recommended for procurement"
    if risk_level == MEDIUM_RISK:
        return "Recommended with monitoring"
    return "Not recommended for critical procurement"


def rank_vendors_by_reliability(vendor_scores: list[dict]) -> list[dict]:
    """Return vendor data sorted by reliability, with one-based rank positions."""
    for vendor in vendor_scores:
        _validate_score(vendor["reliability_score"])
    ranked = sorted(vendor_scores, key=lambda vendor: vendor["reliability_score"], reverse=True)
    return [{**vendor, "rank_position": index} for index, vendor in enumerate(ranked, start=1)]


def analyze_reliability_trend(score_history: list[float]) -> str:
    """Determine the overall direction from the first and latest score."""
    for score in score_history:
        _validate_score(score)
    if len(score_history) < 2:
        return TREND_INSUFFICIENT_DATA
    difference = score_history[-1] - score_history[0]
    if difference >= 5:
        return TREND_IMPROVING
    if difference <= -5:
        return TREND_DECLINING
    return TREND_STABLE


def calculate_average_reliability_score(scores: list[float]) -> float:
    """Calculate a safe, rounded average reliability score."""
    for score in scores:
        _validate_score(score)
    return round(sum(scores) / len(scores), 2) if scores else 0


def count_vendors_by_risk(vendor_scores: list[dict]) -> dict:
    """Count vendors in the Module 5 procurement risk bands."""
    counts = {"low_risk_count": 0, "medium_risk_count": 0, "high_risk_count": 0}
    for vendor in vendor_scores:
        risk_level = classify_procurement_risk(vendor["reliability_score"])
        if risk_level == LOW_RISK:
            counts["low_risk_count"] += 1
        elif risk_level == MEDIUM_RISK:
            counts["medium_risk_count"] += 1
        else:
            counts["high_risk_count"] += 1
    return counts


def should_warn_for_high_risk_vendor(risk_level: str) -> bool:
    """Indicate whether a vendor requires a high-risk warning."""
    return risk_level == HIGH_RISK


def filter_recommended_vendors(
    vendor_scores: list[dict], minimum_score: float = 70
) -> list[dict]:
    """Return non-high-risk vendors meeting the requested score threshold."""
    _validate_score(minimum_score)
    recommended = []
    for vendor in vendor_scores:
        score = vendor["reliability_score"]
        _validate_score(score)
        if score >= minimum_score and classify_procurement_risk(score) != HIGH_RISK:
            recommended.append(vendor)
    return sorted(recommended, key=lambda vendor: vendor["reliability_score"], reverse=True)


def compare_vendor_reliability(vendor_a: dict, vendor_b: dict) -> dict:
    """Compare two vendors and return the higher-scoring vendor or a tie."""
    score_a = vendor_a["reliability_score"]
    score_b = vendor_b["reliability_score"]
    _validate_score(score_a)
    _validate_score(score_b)
    if score_a == score_b:
        return {"better_vendor_id": None, "better_vendor_name": "Tie", "score_difference": 0}
    better_vendor, lower_score = (vendor_a, score_b) if score_a > score_b else (vendor_b, score_a)
    return {
        "better_vendor_id": better_vendor["vendor_id"],
        "better_vendor_name": better_vendor["vendor_name"],
        "score_difference": round(abs(score_a - score_b), 2),
    }
def recalculate_vendor_reliability(
    delivery_score: float | None = None,
    quality_score: float | None = None,
    communication_score: float | None = None,
    issue_resolution_score: float | None = None,
    procurement_history_score: float | None = None,
    contract_compliance_score: float | None = None,
) -> float:
    """
    Compatibility wrapper for API/router imports.

    Recalculates vendor reliability using the confirmed Module 5 scoring helper.
    Missing component scores are excluded and available weights are re-normalized.
    """
    return calculate_vendor_reliability_score(
        delivery_score=delivery_score,
        quality_score=quality_score,
        communication_score=communication_score,
        issue_resolution_score=issue_resolution_score,
        procurement_history_score=procurement_history_score,
        contract_compliance_score=contract_compliance_score,
    )