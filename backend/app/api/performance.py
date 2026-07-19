from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.performance import PerformanceRecord
from app.models.vendor import Vendor
from app.schemas.performance import (
    DeliveryPerformanceCreate,
    QualityPerformanceCreate,
    CommunicationPerformanceCreate,
    ServiceRatingCreate,
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
    calculate_on_time_delivery_rate,
    calculate_delayed_delivery_count,
    calculate_average_quality_score,
    calculate_average_response_time,
    calculate_order_completion_rate,
    generate_vendor_ranking,
)

router = APIRouter(prefix="/performance", tags=["Performance"])


def performance_record_response(record: PerformanceRecord):
    return {
        "id": record.id,
        "vendor_id": record.vendor_id,
        "procurement_order_id": record.procurement_order_id,
        "on_time_delivery": record.on_time_delivery,
        "quality_rating": record.quality_rating,
        "communication_score": record.communication_score,
        "service_rating_score": record.compliance_score,
        "overall_score": record.overall_score,
        "risk_level": record.risk_level,
        "evaluation_date": record.evaluation_date,
        "notes": record.notes,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


@router.get("/dashboard", response_model=PerformanceDashboardOut)
def performance_dashboard(db: Session = Depends(get_db)):
    records = db.query(PerformanceRecord).all()
    total_vendors = len({record.vendor_id for record in records})
    average_overall_score = (
        sum((record.overall_score or 0) for record in records) / len(records)
        if records
        else 0.0
    )
    delivery_scores = [record.on_time_delivery or 0.0 for record in records]
    quality_scores = [record.quality_rating or 0.0 for record in records]
    communication_scores = [record.communication_score or 0.0 for record in records]
    service_scores = [record.compliance_score or 0.0 for record in records]
    excellent_count = sum(1 for record in records if get_performance_status(record.overall_score or 0) == "Excellent")
    good_count = sum(1 for record in records if get_performance_status(record.overall_score or 0) == "Good")
    average_count = sum(1 for record in records if get_performance_status(record.overall_score or 0) == "Average")
    poor_count = sum(1 for record in records if get_performance_status(record.overall_score or 0) == "Poor")
    completion_rate = calculate_order_completion_rate(
        len(records),
        sum(1 for record in records if (record.overall_score or 0) >= 60),
    )

    return {
        "total_vendors": total_vendors,
        "average_overall_score": average_overall_score,
        "excellent_count": excellent_count,
        "good_count": good_count,
        "average_count": average_count,
        "poor_count": poor_count,
        "average_delivery_score": calculate_average_response_time(delivery_scores) if delivery_scores else 0.0,
        "average_quality_score": calculate_average_quality_score(quality_scores) if quality_scores else 0.0,
        "average_communication_score": calculate_average_response_time(communication_scores) if communication_scores else 0.0,
        "average_service_rating_score": calculate_average_response_time(service_scores) if service_scores else 0.0,
        "completion_rate": completion_rate,
    }


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


@router.post("/delivery", response_model=PerformanceActionResponse)
def record_delivery_performance(payload: DeliveryPerformanceCreate, db: Session = Depends(get_db)):
    delay_days = calculate_delivery_delay(payload.expected_delivery_date, payload.actual_delivery_date)
    delivery_status = get_delivery_status(payload.expected_delivery_date, payload.actual_delivery_date)
    delivery_score = calculate_delivery_score(delay_days)
    overall_score = calculate_overall_performance_score(delivery_score, 0, 0, 0)
    performance_status = get_performance_status(overall_score)

    record = PerformanceRecord(
        vendor_id=payload.vendor_id,
        procurement_order_id=payload.purchase_order_id,
        on_time_delivery=delivery_score,
        overall_score=overall_score,
        risk_level=performance_status,
        evaluation_date=payload.actual_delivery_date,
        notes=f"Delivery {delivery_status}, delay {delay_days} days",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "vendor_id": payload.vendor_id,
        "purchase_order_id": payload.purchase_order_id,
        "overall_score": overall_score,
        "performance_status": performance_status,
        "notes": record.notes,
        "evaluation_date": record.evaluation_date,
    }


@router.post("/quality", response_model=PerformanceActionResponse)
def record_quality_performance(payload: QualityPerformanceCreate, db: Session = Depends(get_db)):
    quality_score = calculate_quality_score(
        payload.material_quality,
        payload.packaging_quality,
        payload.quantity_accuracy,
        payload.specification_compliance,
        payload.product_defects,
    )
    overall_score = calculate_overall_performance_score(0, quality_score, 0, 0)
    performance_status = get_performance_status(overall_score)

    record = PerformanceRecord(
        vendor_id=payload.vendor_id,
        procurement_order_id=payload.purchase_order_id,
        quality_rating=quality_score,
        overall_score=overall_score,
        risk_level=performance_status,
        evaluation_date=datetime.utcnow(),
        notes=f"Quality score generated with defects={payload.product_defects}",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "vendor_id": payload.vendor_id,
        "purchase_order_id": payload.purchase_order_id,
        "overall_score": overall_score,
        "performance_status": performance_status,
        "notes": record.notes,
        "evaluation_date": record.evaluation_date,
    }


@router.post("/communication", response_model=PerformanceActionResponse)
def record_communication_performance(payload: CommunicationPerformanceCreate, db: Session = Depends(get_db)):
    response_duration = calculate_response_duration_minutes(payload.message_sent_time, payload.vendor_response_time)
    communication_score = calculate_communication_score(response_duration)
    overall_score = calculate_overall_performance_score(0, 0, communication_score, 0)
    performance_status = get_performance_status(overall_score)

    record = PerformanceRecord(
        vendor_id=payload.vendor_id,
        procurement_order_id=payload.purchase_order_id,
        communication_score=communication_score,
        overall_score=overall_score,
        risk_level=performance_status,
        evaluation_date=datetime.utcnow(),
        notes=f"Response duration {response_duration} minutes",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "vendor_id": payload.vendor_id,
        "purchase_order_id": payload.purchase_order_id,
        "overall_score": overall_score,
        "performance_status": performance_status,
        "notes": record.notes,
        "evaluation_date": record.evaluation_date,
    }


@router.post("/service-rating", response_model=PerformanceActionResponse)
def record_service_rating(payload: ServiceRatingCreate, db: Session = Depends(get_db)):
    service_rating_score = calculate_service_rating_score(
        payload.professionalism,
        payload.customer_support,
        payload.documentation_quality,
        payload.flexibility,
        payload.communication_effectiveness,
        payload.issue_resolution,
    )
    overall_score = calculate_overall_performance_score(0, 0, 0, service_rating_score)
    performance_status = get_performance_status(overall_score)

    record = PerformanceRecord(
        vendor_id=payload.vendor_id,
        procurement_order_id=payload.purchase_order_id,
        compliance_score=service_rating_score,
        overall_score=overall_score,
        risk_level=performance_status,
        evaluation_date=datetime.utcnow(),
        notes="Service rating recorded",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "vendor_id": payload.vendor_id,
        "purchase_order_id": payload.purchase_order_id,
        "overall_score": overall_score,
        "performance_status": performance_status,
        "notes": record.notes,
        "evaluation_date": record.evaluation_date,
    }


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
    records = db.query(PerformanceRecord).all()
    vendor_scores = {}
    for record in records:
        vendor_scores.setdefault(record.vendor_id, []).append(record.overall_score or 0.0)

    average_scores = {
        vendor_id: sum(scores) / len(scores)
        for vendor_id, scores in vendor_scores.items()
    }
    ranking_input = [
        {"vendor_id": vendor_id, "overall_score": score}
        for vendor_id, score in average_scores.items()
    ]
    ranking_list = generate_vendor_ranking(ranking_input)
    result = []
    for idx, item in enumerate(ranking_list, start=1):
        vendor_id = item.get("vendor_id") if isinstance(item, dict) else getattr(item, "vendor_id", None)
        overall_score = item.get("overall_score") if isinstance(item, dict) else getattr(item, "overall_score", 0.0)
        rank = item.get("rank", idx) if isinstance(item, dict) else idx
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first() if vendor_id is not None else None
        result.append(
            {
                "vendor_id": vendor_id or 0,
                "vendor_name": vendor.full_name if vendor else None,
                "overall_score": overall_score or 0.0,
                "rank": rank,
            }
        )
    return {"rankings": result}
