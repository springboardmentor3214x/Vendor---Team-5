from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime

from app.utils.constants import RISK_LOW, RISK_MEDIUM, RISK_HIGH
from app.models.vendor import Vendor
from app.models.delivery_performance import DeliveryPerformance
from app.models.product_quality_evaluation import ProductQualityEvaluation
from app.models.communication_log import CommunicationLog
from app.models.contract import Contract
from app.models.service_rating import ServiceRating
from app.models.performance import PerformanceRecord
from app.models.vendor_ranking import VendorRanking
from app.models.reliability import VendorReliability, PerformanceTrend, ProcurementRecommendation
from app.services.performance_service import calculate_communication_score


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
    for score_component in (
        on_time_delivery_rate,
        quality_rating,
        response_score,
        contract_compliance,
        issue_resolution_score,
    ):
        _validate_score(score_component)

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


def recalculate_vendor_reliability(vendor_id: int, db: Session) -> VendorReliability:
    """
    Collect performance metrics, calculate the reliability score, and update
    reliability tables, vendor rankings, trend analysis, and recommendations.
    """
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise ValueError(f"Vendor with ID {vendor_id} does not exist.")

    # Retrieve latest performance summary to fall back on if raw logs are missing
    pr = db.query(PerformanceRecord).filter(
        PerformanceRecord.vendor_id == vendor_id
    ).order_by(PerformanceRecord.evaluation_date.desc()).first()

    # 1. Delivery Score (30%)
    dp_count = db.query(func.count(DeliveryPerformance.id)).filter(
        DeliveryPerformance.vendor_id == vendor_id
    ).scalar() or 0

    if dp_count > 0:
        on_time_count = db.query(func.count(DeliveryPerformance.id)).filter(
            DeliveryPerformance.vendor_id == vendor_id,
            DeliveryPerformance.delivery_status.in_(["Early Delivery", "On-Time Delivery"])
        ).scalar() or 0
        delivery_score = round((on_time_count / dp_count) * 100, 2)
    elif pr is not None and pr.on_time_delivery_rate is not None:
        delivery_score = pr.on_time_delivery_rate
    else:
        delivery_score = 100.0

    # 2. Product Quality Score (25%)
    pq_count = db.query(func.count(ProductQualityEvaluation.id)).filter(
        ProductQualityEvaluation.vendor_id == vendor_id
    ).scalar() or 0

    if pq_count > 0:
        avg_quality = db.query(func.avg(ProductQualityEvaluation.overall_quality_rating)).filter(
            ProductQualityEvaluation.vendor_id == vendor_id
        ).scalar() or 5.0
        quality_score = round(float(avg_quality) * 20.0, 2)
    elif pr is not None and pr.average_quality_score is not None and pr.average_quality_score > 0:
        quality_score = round(pr.average_quality_score * 20.0, 2)
    else:
        quality_score = 100.0

    # 3. Communication Score (15%)
    comm_count = db.query(func.count(CommunicationLog.id)).filter(
        CommunicationLog.vendor_id == vendor_id,
        CommunicationLog.response_duration_minutes.isnot(None)
    ).scalar() or 0

    if comm_count > 0:
        avg_duration = db.query(func.avg(CommunicationLog.response_duration_minutes)).filter(
            CommunicationLog.vendor_id == vendor_id,
            CommunicationLog.response_duration_minutes.isnot(None)
        ).scalar() or 0
        communication_score = calculate_communication_score(float(avg_duration))
    elif pr is not None and pr.average_response_time is not None and pr.average_response_time > 0:
        communication_score = calculate_communication_score(pr.average_response_time)
    else:
        communication_score = 100.0

    # 4. Contract Compliance (20%)
    contract_count = db.query(func.count(Contract.id)).filter(
        Contract.vendor_id == vendor_id
    ).scalar() or 0

    if contract_count > 0:
        verified_count = db.query(func.count(Contract.id)).filter(
            Contract.vendor_id == vendor_id,
            Contract.compliance_verified == True
        ).scalar() or 0
        compliance_score = round((verified_count / contract_count) * 100, 2)
    else:
        compliance_score = 100.0

    # 5. Issue Resolution Score (10%)
    sr_count = db.query(func.count(ServiceRating.id)).filter(
        ServiceRating.vendor_id == vendor_id,
        ServiceRating.issue_resolution.isnot(None)
    ).scalar() or 0

    if sr_count > 0:
        avg_issue_res = db.query(func.avg(ServiceRating.issue_resolution)).filter(
            ServiceRating.vendor_id == vendor_id,
            ServiceRating.issue_resolution.isnot(None)
        ).scalar() or 5.0
        issue_resolution_score = round(float(avg_issue_res) * 20.0, 2)
    else:
        issue_resolution_score = 100.0

    # Calculate final score
    reliability_score = calculate_reliability_score(
        delivery_score,
        quality_score,
        communication_score,
        compliance_score,
        issue_resolution_score
    )

    risk_level = get_risk_level(reliability_score)
    recommendation = generate_vendor_recommendation(reliability_score)

    # 6. Update Vendor Table
    vendor.reliability_score = reliability_score

    # 7. Update Vendor Reliability Details
    rel = db.query(VendorReliability).filter(VendorReliability.vendor_id == vendor_id).first()
    if not rel:
        rel = VendorReliability(vendor_id=vendor_id)
        db.add(rel)

    rel.delivery_score = delivery_score
    rel.quality_score = quality_score
    rel.communication_score = communication_score
    rel.compliance_score = compliance_score
    rel.issue_resolution_score = issue_resolution_score
    rel.reliability_score = reliability_score
    rel.risk_level = risk_level
    rel.recommendation = recommendation
    rel.updated_at = datetime.utcnow()

    # 8. Record Monthly Performance Trend
    now = datetime.utcnow()
    trend = db.query(PerformanceTrend).filter(
        PerformanceTrend.vendor_id == vendor_id,
        PerformanceTrend.year == now.year,
        PerformanceTrend.month == now.month
    ).first()

    if not trend:
        trend = PerformanceTrend(
            vendor_id=vendor_id,
            year=now.year,
            month=now.month
        )
        db.add(trend)

    trend.reliability_score = reliability_score
    trend.delivery_score = delivery_score
    trend.quality_score = quality_score
    trend.communication_score = communication_score
    trend.compliance_score = compliance_score
    trend.issue_resolution_score = issue_resolution_score

    # 9. Update Procurement Recommendation
    rec = db.query(ProcurementRecommendation).filter(
        ProcurementRecommendation.vendor_id == vendor_id
    ).first()

    if not rec:
        rec = ProcurementRecommendation(vendor_id=vendor_id)
        db.add(rec)

    rec.reliability_score = reliability_score
    rec.risk_level = risk_level
    if reliability_score >= 80:
        rec.recommendation_status = "Recommended"
        rec.reason = "Vendor shows high delivery rate, strong product quality, and verified compliance."
    elif reliability_score >= 50:
        rec.recommendation_status = "Monitor"
        rec.reason = "Vendor has moderate reliability ratings. Monitor delivery delays and response times."
    else:
        rec.recommendation_status = "Not Recommended"
        rec.reason = "High risk vendor with repeat performance issues or low compliance rate."
    rec.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(rel)

    # 10. Update Supplier Rankings
    recalculate_supplier_rankings(db)

    return rel


def recalculate_supplier_rankings(db: Session) -> None:
    """
    Ranks all vendors by reliability score in descending order and updates VendorRanking.
    """
    all_rel = db.query(VendorReliability).order_by(VendorReliability.reliability_score.desc()).all()
    for idx, rel in enumerate(all_rel, start=1):
        ranking = db.query(VendorRanking).filter(VendorRanking.vendor_id == rel.vendor_id).first()
        if not ranking:
            ranking = VendorRanking(vendor_id=rel.vendor_id)
            db.add(ranking)

        ranking.overall_performance_score = rel.reliability_score
        ranking.delivery_score = rel.delivery_score
        ranking.quality_score = rel.quality_score
        ranking.communication_score = rel.communication_score
        ranking.service_rating_score = rel.issue_resolution_score
        ranking.rank_position = idx

    db.commit()