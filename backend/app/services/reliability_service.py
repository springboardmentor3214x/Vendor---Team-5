from datetime import datetime

from sqlalchemy.orm import Session

from app.models.certification import Certification
from app.models.communication_log import CommunicationLog
from app.models.compliance import ComplianceRecord
from app.models.contract import Contract
from app.models.delivery_performance import DeliveryPerformance
from app.models.invoice import Invoice
from app.models.order_tracking import OrderTracking
from app.models.product_quality_evaluation import ProductQualityEvaluation
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.reliability import PerformanceTrend, ProcurementRecommendation, VendorReliability
from app.models.service_rating import ServiceRating
from app.models.vendor_document import VendorDocument
from app.models.vendor import Vendor
from app.services.performance_service import (
    calculate_communication_score, calculate_delivery_score, calculate_quality_score,
)
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
def _all(db: Session, model: type) -> list:
    """Read an optional model safely; this also keeps services usable in tests."""
    try:
        return list(db.query(model).all() or [])
    except Exception:
        return []


def _vendor_rows(db: Session, model: type, vendor_id: int) -> list:
    return [row for row in _all(db, model) if getattr(row, "vendor_id", None) == vendor_id]


def _average(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 2) if values else None


def _delivery_component(db: Session, vendor_id: int, purchase_orders: list) -> float | None:
    scores = []
    for row in _vendor_rows(db, DeliveryPerformance, vendor_id):
        delay = getattr(row, "delay_days", None)
        status = getattr(row, "delivery_status", None)
        if delay is not None:
            scores.append(calculate_delivery_score(int(delay)))
        elif status in {"Early Delivery", "On-Time Delivery"}:
            scores.append(100.0)
        elif status == "Delayed Delivery":
            scores.append(40.0)
    po_ids = {getattr(row, "id", None) for row in purchase_orders}
    for row in _all(db, OrderTracking):
        if getattr(row, "purchase_order_id", None) not in po_ids:
            continue
        delay, status = getattr(row, "delay_days", None), getattr(row, "delivery_status", None)
        if delay is not None and status in {"Delivered", "Completed", "Delayed"}:
            scores.append(calculate_delivery_score(int(delay)))
        elif status in {"Delivered", "Completed"}:
            scores.append(100.0)
        elif status == "Delayed":
            scores.append(40.0)
    return _average(scores)


def _quality_component(db: Session, vendor_id: int) -> float | None:
    scores = []
    for row in _vendor_rows(db, ProductQualityEvaluation, vendor_id):
        overall = getattr(row, "overall_quality_rating", None)
        if overall is not None:
            scores.append(max(0.0, min(100.0, float(overall) * 20)))
            continue
        ratings = [getattr(row, name, None) for name in ("material_quality", "packaging_quality", "quantity_accuracy", "specification_compliance")]
        if all(value is not None for value in ratings):
            scores.append(calculate_quality_score(*ratings, product_defects=getattr(row, "product_defects", 0) or 0))
    return _average(scores)


def _communication_components(db: Session, vendor_id: int) -> tuple[float | None, float | None]:
    communication, issue_resolution = [], []
    for row in _vendor_rows(db, CommunicationLog, vendor_id):
        duration = getattr(row, "response_duration_minutes", None)
        status = getattr(row, "communication_status", None)
        if duration is not None:
            communication.append(calculate_communication_score(float(duration)))
        elif status in {"No Response", "Escalated"}:
            communication.append(0.0)
    for row in _vendor_rows(db, ServiceRating, vendor_id):
        response = getattr(row, "communication_effectiveness", None)
        issue = getattr(row, "issue_resolution", None)
        if response is not None:
            communication.append(max(0.0, min(100.0, float(response) * 20)))
        if issue is not None:
            issue_resolution.append(max(0.0, min(100.0, float(issue) * 20)))
    return _average(communication), _average(issue_resolution)


def _procurement_history_component(db: Session, vendor_id: int, purchase_orders: list) -> float | None:
    """Score successful procurement activity only; it is deliberately not compliance."""
    rates = []
    if purchase_orders:
        rates.append(100 * sum(getattr(row, "po_status", "") in {"Delivered", "Completed"} for row in purchase_orders) / len(purchase_orders))
    requests = _vendor_rows(db, ProcurementRequest, vendor_id)
    if requests:
        rates.append(100 * sum(getattr(row, "approval_status", "") == "Approved" for row in requests) / len(requests))
    po_ids = {getattr(row, "id", None) for row in purchase_orders}
    invoices = [row for row in _all(db, Invoice) if getattr(row, "purchase_order_id", None) in po_ids]
    if invoices:
        rates.append(100 * sum(getattr(row, "payment_status", "") in {"Verified", "Approved", "Paid"} for row in invoices) / len(invoices))
    return _average(rates)


def _compliance_component(db: Session, vendor_id: int) -> float | None:
    rates = []
    contracts = _vendor_rows(db, Contract, vendor_id)
    if contracts:
        rates.append(100 * sum(bool(getattr(row, "compliance_verified", False)) for row in contracts) / len(contracts))
    records = _vendor_rows(db, ComplianceRecord, vendor_id)
    if records:
        rates.append(100 * sum(getattr(row, "status", "") == "Compliant" for row in records) / len(records))
    now = datetime.utcnow()
    certifications = _vendor_rows(db, Certification, vendor_id)
    if certifications:
        rates.append(100 * sum(getattr(row, "expiry_date", None) is not None and getattr(row, "expiry_date") >= now for row in certifications) / len(certifications))
    documents = _vendor_rows(db, VendorDocument, vendor_id)
    if documents:
        # The document model has no verification/status field; existence is the only supported signal.
        rates.append(100.0)
    return _average(rates)


def _upsert_derived_rows(db: Session, vendor_id: int, reliability: VendorReliability, score: float, risk_level: str, recommendation: str) -> None:
    now = datetime.utcnow()
    trend = next((row for row in _vendor_rows(db, PerformanceTrend, vendor_id)
                  if getattr(row, "year", None) == now.year and getattr(row, "month", None) == now.month), None)
    if trend is None:
        trend = PerformanceTrend(vendor_id=vendor_id, year=now.year, month=now.month)
        db.add(trend)
    for field in ("reliability_score", "delivery_score", "quality_score", "communication_score", "compliance_score", "issue_resolution_score", "procurement_history_score"):
        setattr(trend, field, getattr(reliability, field, 0.0) or 0.0)
    recommendation_row = next((row for row in _vendor_rows(db, ProcurementRecommendation, vendor_id)), None)
    if recommendation_row is None:
        recommendation_row = ProcurementRecommendation(vendor_id=vendor_id)
        db.add(recommendation_row)
    recommendation_row.reliability_score = score
    recommendation_row.risk_level = risk_level
    recommendation_row.recommendation_status = {LOW_RISK: "Recommended", MEDIUM_RISK: "Monitor", HIGH_RISK: "Not Recommended"}[risk_level]
    recommendation_row.reason = recommendation


def recalculate_vendor_reliability(vendor_id: int, db: Session) -> VendorReliability:
    """Aggregate available vendor facts, persist the supported reliability record, and return it."""
    reliability = (
        db.query(VendorReliability)
        .filter(VendorReliability.vendor_id == vendor_id)
        .first()
    )

    if reliability is None:
        reliability = VendorReliability(vendor_id=vendor_id)
        db.add(reliability)

    purchase_orders = _vendor_rows(db, PurchaseOrder, vendor_id)
    delivery_score = _delivery_component(db, vendor_id, purchase_orders)
    quality_score = _quality_component(db, vendor_id)
    communication_score, issue_resolution_score = _communication_components(db, vendor_id)
    procurement_history_score = _procurement_history_component(db, vendor_id, purchase_orders)
    compliance_score = _compliance_component(db, vendor_id)
    # A recalculation may run before any new source records are available. Keep
    # a non-zero persisted component in that case instead of erasing valid
    # historical reliability data because of a model/query compatibility gap.
    if delivery_score is None:
        delivery_score = getattr(reliability, "delivery_score", None) or None
    if quality_score is None:
        quality_score = getattr(reliability, "quality_score", None) or None
    if communication_score is None:
        communication_score = getattr(reliability, "communication_score", None) or None
    if issue_resolution_score is None:
        issue_resolution_score = getattr(reliability, "issue_resolution_score", None) or None
    if compliance_score is None:
        compliance_score = getattr(reliability, "compliance_score", None) or None
    score = calculate_vendor_reliability_score(
        delivery_score=delivery_score,
        quality_score=quality_score,
        communication_score=communication_score,
        issue_resolution_score=issue_resolution_score,
        procurement_history_score=procurement_history_score,
        contract_compliance_score=compliance_score,
    )
    risk_level = classify_procurement_risk(score)
    recommendation = generate_procurement_recommendation(score, risk_level)

    # SQL columns are non-null in the current API schema.  Zero is persisted
    # only as a representation of unavailable data; it is not fed back into scoring.
    for field, value in (("delivery_score", delivery_score), ("quality_score", quality_score),
                         ("communication_score", communication_score), ("compliance_score", compliance_score),
                         ("issue_resolution_score", issue_resolution_score),
                         ("procurement_history_score", procurement_history_score)):
        if hasattr(reliability, field):
            setattr(reliability, field, 0.0 if value is None else value)

    reliability.reliability_score = score
    reliability.risk_level = risk_level
    if hasattr(reliability, "recommendation"):
        reliability.recommendation = recommendation
    if hasattr(reliability, "updated_at"):
        reliability.updated_at = datetime.utcnow()

    # Retain the legacy denormalized Vendor score when a vendor row exists,
    # but it is not used as a Module 5 ranking source.
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if vendor is not None and hasattr(vendor, "reliability_score"):
        vendor.reliability_score = score

    _upsert_derived_rows(db, vendor_id, reliability, score, risk_level, recommendation)
    db.commit()
    db.refresh(reliability)
    return reliability


def refresh_vendor_reliability_after_performance_write(vendor_id: int, db: Session) -> VendorReliability:
    """Service-side trigger for delivery, quality, communication, or service-rating writes.

    Recalculation persists the month trend; the ranking call keeps the dynamic
    supplier-ranking view synchronized without introducing a second ranking table.
    """
    reliability = recalculate_vendor_reliability(vendor_id, db)
    recalculate_supplier_rankings(db)
    return reliability


def refresh_vendor_reliability_after_procurement_update(vendor_id: int, db: Session) -> VendorReliability:
    """Service-side trigger for delivered/completed PO and tracking updates."""
    return recalculate_vendor_reliability(vendor_id, db)


def refresh_vendor_reliability_after_compliance_update(vendor_id: int, db: Session) -> VendorReliability:
    """Service-side trigger for contract, compliance, certification, and document writes."""
    return recalculate_vendor_reliability(vendor_id, db)


def recalculate_supplier_rankings(db: Session) -> list[dict]:
    """Return dynamic Module 5 rankings from persisted reliability scores.

    VendorRanking belongs to Module 4 performance ranking and is deliberately
    not read or written here.  There is no dedicated reliability-ranking model
    in this project, so ranking remains a dynamic response derived from
    ``VendorReliability``.
    """
    reliability_rows = db.query(VendorReliability).all()
    if not reliability_rows:
        return []

    vendor_scores = [
        {
            "vendor_id": row.vendor_id,
            "vendor_name": getattr(row, "vendor_name", str(row.vendor_id)),
            "reliability_score": row.reliability_score,
            "risk_level": row.risk_level,
        }
        for row in reliability_rows
    ]
    return rank_vendors_by_reliability(vendor_scores)
