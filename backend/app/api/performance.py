from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.performance import PerformanceRecord
from app.models.delivery_performance import DeliveryPerformance
from app.models.product_quality_evaluation import ProductQualityEvaluation
from app.models.communication_log import CommunicationLog
from app.models.service_rating import ServiceRating
from app.models.vendor_ranking import VendorRanking
from app.models.vendor import Vendor
from app.models.user import User

from app.schemas.performance import (
    DeliveryPerformanceCreate,
    DeliveryPerformanceOut,
    QualityPerformanceCreate,
    QualityPerformanceOut,
    CommunicationPerformanceCreate,
    CommunicationPerformanceOut,
    ServiceRatingCreate,
    ServiceRatingOut,
    PerformanceActionResponse,
    PerformanceDashboardOut,
    PerformanceRecordOut,
    VendorRankingOut,
)
from app.services.performance_service import (
    calculate_delivery_delay,
    get_delivery_status,
    calculate_delivery_score,
    calculate_quality_score,
    calculate_response_duration_minutes,
    calculate_communication_score,
    calculate_service_rating_score,
    calculate_overall_performance_score,
    get_performance_status,
    calculate_average_delivery_score,
    calculate_average_quality_score,
    calculate_average_communication_score,
    calculate_average_service_rating_score,
    calculate_order_completion_rate,
    can_user_recalculate_vendor_ranking,
    validate_no_duplicate_performance_entry,
    validate_performance_write_eligibility,
)

router = APIRouter(prefix="/performance", tags=["Performance"])


def performance_record_response(record: PerformanceRecord):
    return {
        "id": record.id,
        "vendor_id": record.vendor_id,
        "total_completed_orders": record.total_completed_orders,
        "on_time_delivery_rate": record.on_time_delivery_rate,
        "delayed_delivery_count": record.delayed_delivery_count,
        "average_quality_score": record.average_quality_score,
        "average_response_time": record.average_response_time,
        "average_service_rating_score": record.average_service_rating_score,
        "overall_performance_score": record.overall_performance_score,
        "performance_status": record.performance_status,
        "evaluation_date": record.evaluation_date,
        "notes": record.notes,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


def get_or_create_record(db: Session, vendor_id: int) -> PerformanceRecord:
    record = db.query(PerformanceRecord).filter(PerformanceRecord.vendor_id == vendor_id).first()
    if not record:
        record = PerformanceRecord(
            vendor_id=vendor_id,
            total_completed_orders=0,
            on_time_delivery_rate=0.0,
            delayed_delivery_count=0,
            average_quality_score=0.0,
            average_response_time=0.0,
            average_service_rating_score=0.0,
            overall_performance_score=0.0,
            performance_status="Average",
            evaluation_date=datetime.utcnow(),
            notes=None,
        )
        db.add(record)
        db.flush()
    return record


def sync_overall_score(record: PerformanceRecord) -> None:
    record.overall_performance_score = calculate_overall_performance_score(
        record.on_time_delivery_rate or 0.0,
        record.average_quality_score or 0.0,
        record.average_response_time or 0.0,
        record.average_service_rating_score or 0.0,
    )
    record.performance_status = get_performance_status(record.overall_performance_score)


def refresh_vendor_ranking(db: Session, vendor_id: int) -> None:
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        return

    record = db.query(PerformanceRecord).filter(PerformanceRecord.vendor_id == vendor_id).first()
    if not record:
        return

    ranking = db.query(VendorRanking).filter(VendorRanking.vendor_id == vendor_id).first()
    if not ranking:
        ranking = VendorRanking(
            vendor_id=vendor_id,
            delivery_score=record.on_time_delivery_rate or 0.0,
            quality_score=record.average_quality_score or 0.0,
            communication_score=record.average_response_time or 0.0,
            service_rating_score=record.average_service_rating_score or 0.0,
            overall_performance_score=record.overall_performance_score or 0.0,
            rank_position=0,
        )
        db.add(ranking)
    else:
        ranking.delivery_score = record.on_time_delivery_rate or 0.0
        ranking.quality_score = record.average_quality_score or 0.0
        ranking.communication_score = record.average_response_time or 0.0
        ranking.service_rating_score = record.average_service_rating_score or 0.0
        ranking.overall_performance_score = record.overall_performance_score or 0.0

    db.flush()

    all_rankings = (
        db.query(VendorRanking)
        .order_by(VendorRanking.overall_performance_score.desc())
        .all()
    )
    for idx, item in enumerate(all_rankings, start=1):
        item.rank_position = idx


@router.get("/dashboard", response_model=PerformanceDashboardOut)
def performance_dashboard(db: Session = Depends(get_db)):
    records = db.query(PerformanceRecord).all()
    total_vendors = len({record.vendor_id for record in records})

    average_overall_score = (
        sum((r.overall_performance_score or 0.0) for r in records) / len(records) if records else 0.0
    )

    delivery_scores = [r.on_time_delivery_rate or 0.0 for r in records]
    quality_scores = [r.average_quality_score or 0.0 for r in records]
    response_scores = [r.average_response_time or 0.0 for r in records]
    service_scores = [r.average_service_rating_score or 0.0 for r in records]

    excellent_count = sum(1 for r in records if get_performance_status(r.overall_performance_score or 0.0) == "Excellent")
    good_count = sum(1 for r in records if get_performance_status(r.overall_performance_score or 0.0) == "Good")
    average_count = sum(1 for r in records if get_performance_status(r.overall_performance_score or 0.0) == "Average")
    poor_count = sum(1 for r in records if get_performance_status(r.overall_performance_score or 0.0) == "Poor")

    total_completed = sum(r.total_completed_orders or 0 for r in records)
    total_delayed = sum(r.delayed_delivery_count or 0 for r in records)

    completion_rate = calculate_order_completion_rate(
        len(records),
        sum(1 for r in records if (r.overall_performance_score or 0.0) >= 60),
    )

    return {
        "total_vendors": total_vendors,
        "average_overall_score": average_overall_score,
        "excellent_count": excellent_count,
        "good_count": good_count,
        "average_count": average_count,
        "poor_count": poor_count,
        "total_completed_orders": total_completed,
        "total_delayed_deliveries": total_delayed,
        "average_delivery_score": calculate_average_delivery_score(delivery_scores),
        "average_quality_score": calculate_average_quality_score(quality_scores) if quality_scores else 0.0,
        "average_communication_score": calculate_average_communication_score(response_scores),
        "average_service_rating_score": calculate_average_service_rating_score(service_scores),
        "completion_rate": completion_rate,
    }


@router.post("/delivery", response_model=PerformanceActionResponse)
def record_delivery_performance(payload: DeliveryPerformanceCreate, db: Session = Depends(get_db)):
    try:
        validate_performance_write_eligibility(db, payload.vendor_id, payload.purchase_order_id)
        validate_no_duplicate_performance_entry(db, DeliveryPerformance, payload.vendor_id, payload.purchase_order_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    delay_days = calculate_delivery_delay(payload.expected_delivery_date, payload.actual_delivery_date)
    delivery_status = get_delivery_status(payload.expected_delivery_date, payload.actual_delivery_date)
    delivery_score = calculate_delivery_score(delay_days)

    delivery_entry = DeliveryPerformance(
        purchase_order_id=payload.purchase_order_id,
        vendor_id=payload.vendor_id,
        expected_delivery_date=payload.expected_delivery_date,
        actual_delivery_date=payload.actual_delivery_date,
        delay_days=delay_days,
        delivery_status=delivery_status,
        remarks=payload.remarks,
    )
    db.add(delivery_entry)

    record = get_or_create_record(db, payload.vendor_id)
    previous_orders = record.total_completed_orders or 0
    previous_on_time_rate = record.on_time_delivery_rate or 0.0
    previous_delayed_count = record.delayed_delivery_count or 0

    new_total_orders = previous_orders + 1
    new_delayed_count = previous_delayed_count + (0 if delay_days <= 0 else 1)
    new_on_time_rate = ((previous_on_time_rate * previous_orders) + delivery_score) / new_total_orders

    record.total_completed_orders = new_total_orders
    record.on_time_delivery_rate = new_on_time_rate
    record.delayed_delivery_count = new_delayed_count
    record.evaluation_date = payload.actual_delivery_date
    record.notes = f"PO {payload.purchase_order_id}: Delivery {delivery_status}, delay {delay_days} days"
    sync_overall_score(record)

    refresh_vendor_ranking(db, payload.vendor_id)
    db.commit()
    db.refresh(record)

    return {
        "vendor_id": payload.vendor_id,
        "purchase_order_id": payload.purchase_order_id,
        "overall_score": record.overall_performance_score,
        "performance_status": record.performance_status,
        "notes": record.notes,
        "evaluation_date": record.evaluation_date,
    }


@router.get("/delivery/{vendor_id}", response_model=list[DeliveryPerformanceOut])
def list_delivery_performance(vendor_id: int, db: Session = Depends(get_db)):
    return (
        db.query(DeliveryPerformance)
        .filter(DeliveryPerformance.vendor_id == vendor_id)
        .order_by(DeliveryPerformance.actual_delivery_date.desc())
        .all()
    )


@router.post("/quality", response_model=PerformanceActionResponse)
def record_quality_performance(payload: QualityPerformanceCreate, db: Session = Depends(get_db)):
    try:
        validate_performance_write_eligibility(db, payload.vendor_id, payload.purchase_order_id)
        validate_no_duplicate_performance_entry(db, ProductQualityEvaluation, payload.vendor_id, payload.purchase_order_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    quality_score = calculate_quality_score(
        payload.material_quality,
        payload.packaging_quality,
        payload.quantity_accuracy,
        payload.specification_compliance,
        payload.product_defects,
    )

    quality_entry = ProductQualityEvaluation(
        purchase_order_id=payload.purchase_order_id,
        vendor_id=payload.vendor_id,
        inspection_date=payload.inspection_date or datetime.utcnow(),
        material_quality=payload.material_quality,
        packaging_quality=payload.packaging_quality,
        quantity_accuracy=payload.quantity_accuracy,
        specification_compliance=payload.specification_compliance,
        product_defects=payload.product_defects,
        overall_quality_rating=quality_score,
        inspector_remarks=payload.inspector_remarks,
    )
    db.add(quality_entry)

    record = get_or_create_record(db, payload.vendor_id)
    record.average_quality_score = quality_score
    record.evaluation_date = datetime.utcnow()
    record.notes = f"PO {payload.purchase_order_id}: Quality score generated with defects={payload.product_defects}"
    sync_overall_score(record)

    refresh_vendor_ranking(db, payload.vendor_id)
    db.commit()
    db.refresh(record)

    return {
        "vendor_id": payload.vendor_id,
        "purchase_order_id": payload.purchase_order_id,
        "overall_score": record.overall_performance_score,
        "performance_status": record.performance_status,
        "notes": record.notes,
        "evaluation_date": record.evaluation_date,
    }


@router.get("/quality/{vendor_id}", response_model=list[QualityPerformanceOut])
def list_quality_performance(vendor_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ProductQualityEvaluation)
        .filter(ProductQualityEvaluation.vendor_id == vendor_id)
        .order_by(ProductQualityEvaluation.inspection_date.desc())
        .all()
    )


@router.post("/communication", response_model=PerformanceActionResponse)
def record_communication_performance(payload: CommunicationPerformanceCreate, db: Session = Depends(get_db)):
    try:
        validate_performance_write_eligibility(db, payload.vendor_id, payload.purchase_order_id)
        validate_no_duplicate_performance_entry(db, CommunicationLog, payload.vendor_id, payload.purchase_order_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    response_duration = int(
        calculate_response_duration_minutes(
            payload.message_sent_time,
            payload.vendor_response_time,
        )
    )
    communication_score = calculate_communication_score(response_duration)

    comm_entry = CommunicationLog(
        purchase_order_id=payload.purchase_order_id,
        vendor_id=payload.vendor_id,
        message_sent_time=payload.message_sent_time,
        vendor_response_time=payload.vendor_response_time,
        response_duration_minutes=response_duration,
        communication_status="Responded",
        remarks=payload.remarks,
    )
    db.add(comm_entry)

    record = get_or_create_record(db, payload.vendor_id)
    record.average_response_time = float(response_duration)
    record.evaluation_date = datetime.utcnow()
    record.notes = f"PO {payload.purchase_order_id}: Response duration {response_duration} minutes"
    sync_overall_score(record)

    refresh_vendor_ranking(db, payload.vendor_id)
    db.commit()
    db.refresh(record)

    return {
        "vendor_id": payload.vendor_id,
        "purchase_order_id": payload.purchase_order_id,
        "overall_score": record.overall_performance_score,
        "performance_status": record.performance_status,
        "notes": record.notes,
        "evaluation_date": record.evaluation_date,
    }


@router.get("/communication/{vendor_id}", response_model=list[CommunicationPerformanceOut])
def list_communication_logs(vendor_id: int, db: Session = Depends(get_db)):
    return (
        db.query(CommunicationLog)
        .filter(CommunicationLog.vendor_id == vendor_id)
        .order_by(CommunicationLog.message_sent_time.desc())
        .all()
    )


@router.post("/service-rating", response_model=PerformanceActionResponse)
def record_service_rating(payload: ServiceRatingCreate, db: Session = Depends(get_db)):
    try:
        validate_performance_write_eligibility(db, payload.vendor_id, payload.purchase_order_id)
        validate_no_duplicate_performance_entry(db, ServiceRating, payload.vendor_id, payload.purchase_order_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    service_rating_score = calculate_service_rating_score(
        payload.professionalism,
        payload.customer_support,
        payload.documentation_quality,
        payload.flexibility,
        payload.communication_effectiveness,
        payload.issue_resolution,
    )

    rating_entry = ServiceRating(
        purchase_order_id=payload.purchase_order_id,
        vendor_id=payload.vendor_id,
        professionalism=payload.professionalism,
        customer_support=payload.customer_support,
        documentation_quality=payload.documentation_quality,
        flexibility=payload.flexibility,
        communication_effectiveness=payload.communication_effectiveness,
        issue_resolution=payload.issue_resolution,
        overall_service_rating=service_rating_score,
        comments=payload.comments,
    )
    db.add(rating_entry)

    record = get_or_create_record(db, payload.vendor_id)
    record.average_service_rating_score = service_rating_score
    record.evaluation_date = datetime.utcnow()
    record.notes = f"PO {payload.purchase_order_id}: Service rating recorded"
    sync_overall_score(record)

    refresh_vendor_ranking(db, payload.vendor_id)
    db.commit()
    db.refresh(record)

    return {
        "vendor_id": payload.vendor_id,
        "purchase_order_id": payload.purchase_order_id,
        "overall_score": record.overall_performance_score,
        "performance_status": record.performance_status,
        "notes": record.notes,
        "evaluation_date": record.evaluation_date,
    }


@router.get("/service-rating/{vendor_id}", response_model=list[ServiceRatingOut])
def list_service_ratings(vendor_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ServiceRating)
        .filter(ServiceRating.vendor_id == vendor_id)
        .order_by(ServiceRating.id.desc())
        .all()
    )


@router.get("/history/{vendor_id}", response_model=list[PerformanceRecordOut])
def performance_history(vendor_id: int, db: Session = Depends(get_db)):
    records = (
        db.query(PerformanceRecord)
        .filter(PerformanceRecord.vendor_id == vendor_id)
        .order_by(PerformanceRecord.evaluation_date.desc())
        .all()
    )
    return [performance_record_response(record) for record in records]


@router.get("/rankings", response_model=VendorRankingOut)
def vendor_rankings(db: Session = Depends(get_db)):
    rankings = (
        db.query(VendorRanking)
        .order_by(VendorRanking.rank_position.asc())
        .all()
    )

    result = []
    for r in rankings:
        vendor = db.query(Vendor).filter(Vendor.id == r.vendor_id).first()
        result.append(
            {
                "vendor_id": r.vendor_id,
                "vendor_name": vendor.company_name if vendor else None,
                "delivery_score": r.delivery_score or 0.0,
                "quality_score": r.quality_score or 0.0,
                "communication_score": r.communication_score or 0.0,
                "service_rating_score": r.service_rating_score or 0.0,
                "overall_performance_score": r.overall_performance_score or 0.0,
                "rank_position": r.rank_position,
            }
        )

    return {"rankings": result}


@router.post("/rankings/recalculate", response_model=VendorRankingOut)
def recalculate_rankings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not can_user_recalculate_vendor_ranking(current_user.role):
        raise HTTPException(
            status_code=403,
            detail="Only Administrator or Procurement Manager can recalculate vendor rankings",
        )
    records = db.query(PerformanceRecord).all()
    for record in records:
        refresh_vendor_ranking(db, record.vendor_id)
    db.commit()
    return vendor_rankings(db)


@router.get("/{vendor_id}", response_model=PerformanceRecordOut)
def get_vendor_performance(vendor_id: int, db: Session = Depends(get_db)):
    record = (
        db.query(PerformanceRecord)
        .filter(PerformanceRecord.vendor_id == vendor_id)
        .order_by(PerformanceRecord.evaluation_date.desc())
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Performance record not found")
    return performance_record_response(record)
