from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user, normalize_user_role
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
    PerformanceHistoryWithIssuesOut,
)
from app.schemas.document_lifecycle import (
    VendorIssueCreate,
    VendorIssueOut,
    VendorIssueResolve,
    VendorIssueUpdate,
)
from app.api.reliability_refresh import refresh_after_performance_write
from app.services import vendor_issue_service
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

_PERFORMANCE_WRITE_ROLES = {"Administrator", "Procurement Manager"}
_PERFORMANCE_READ_ROLES = {
    "Administrator",
    "Procurement Manager",
    "Supply Chain Manager",
    "Auditor",
}


def _require_performance_write_access(current_user: User) -> None:
    if normalize_user_role(current_user) not in _PERFORMANCE_WRITE_ROLES:
        raise HTTPException(
            status_code=403,
            detail="Only Administrators or Procurement Managers can record performance data",
        )


def _require_performance_read_access(current_user: User) -> None:
    if normalize_user_role(current_user) not in _PERFORMANCE_READ_ROLES:
        raise HTTPException(status_code=403, detail="Access denied")


def _require_vendor_performance_access(
    vendor_id: int,
    current_user: User,
    db: Session,
) -> None:
    role = normalize_user_role(current_user)
    if role in _PERFORMANCE_READ_ROLES:
        return
    if role == "Vendor":
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if vendor and vendor.id == vendor_id:
            return
    raise HTTPException(status_code=403, detail="Access denied")


def _issue_response(issue) -> dict:
    """Map the persistence field `issue_category` to the UI's `category`."""
    return {
        "id": issue.id,
        "vendor_id": issue.vendor_id,
        "purchase_order_id": issue.purchase_order_id,
        "category": issue.issue_category,
        "severity": issue.severity,
        "description": issue.description,
        "status": issue.status,
        "reported_by": issue.reported_by,
        "reported_date": issue.reported_date,
        "assigned_to": issue.assigned_to,
        "resolution_notes": issue.resolution_notes,
        "resolved_by": issue.resolved_by,
        "resolved_date": issue.resolved_date,
        "created_at": issue.created_at,
        "updated_at": issue.updated_at,
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


def _communication_score_for_vendor(db: Session, vendor_id: int) -> float:
    """Derive a 0-100 communication score from real communication records.

    ``average_response_time`` is deliberately retained as minutes; it must not
    be used as a performance score.
    """
    response_minutes = [
        row[0]
        for row in db.query(CommunicationLog.response_duration_minutes)
        .filter(CommunicationLog.vendor_id == vendor_id)
        .all()
        if row[0] is not None
    ]
    return calculate_average_communication_score(
        [calculate_communication_score(minutes) for minutes in response_minutes]
    ) if response_minutes else 0.0


def sync_overall_score(db: Session, record: PerformanceRecord) -> None:
    record.overall_performance_score = calculate_overall_performance_score(
        record.on_time_delivery_rate or 0.0,
        record.average_quality_score or 0.0,
        _communication_score_for_vendor(db, record.vendor_id),
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
            communication_score=_communication_score_for_vendor(db, vendor_id),
            service_rating_score=record.average_service_rating_score or 0.0,
            overall_performance_score=record.overall_performance_score or 0.0,
            rank_position=0,
        )
        db.add(ranking)
    else:
        ranking.delivery_score = record.on_time_delivery_rate or 0.0
        ranking.quality_score = record.average_quality_score or 0.0
        ranking.communication_score = _communication_score_for_vendor(db, vendor_id)
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
def performance_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_performance_read_access(current_user)
    records = db.query(PerformanceRecord).all()
    total_vendors = len({record.vendor_id for record in records})

    average_overall_score = (
        sum((r.overall_performance_score or 0.0) for r in records) / len(records) if records else 0.0
    )

    delivery_scores = [r.on_time_delivery_rate or 0.0 for r in records]
    quality_scores = [r.average_quality_score or 0.0 for r in records]
    communication_scores = [_communication_score_for_vendor(db, r.vendor_id) for r in records]
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
        "average_communication_score": calculate_average_communication_score(communication_scores),
        "average_service_rating_score": calculate_average_service_rating_score(service_scores),
        "completion_rate": completion_rate,
    }


@router.post("/delivery", response_model=PerformanceActionResponse)
def record_delivery_performance(
    payload: DeliveryPerformanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_performance_write_access(current_user)
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
    sync_overall_score(db, record)

    refresh_vendor_ranking(db, payload.vendor_id)
    db.commit()
    db.refresh(record)
    refresh_after_performance_write(payload.vendor_id, db)

    return {
        "vendor_id": payload.vendor_id,
        "purchase_order_id": payload.purchase_order_id,
        "overall_score": record.overall_performance_score,
        "performance_status": record.performance_status,
        "notes": record.notes,
        "evaluation_date": record.evaluation_date,
    }


@router.get("/delivery/{vendor_id}", response_model=list[DeliveryPerformanceOut])
def list_delivery_performance(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_vendor_performance_access(vendor_id, current_user, db)
    return (
        db.query(DeliveryPerformance)
        .filter(DeliveryPerformance.vendor_id == vendor_id)
        .order_by(DeliveryPerformance.actual_delivery_date.desc())
        .all()
    )


@router.post("/quality", response_model=PerformanceActionResponse)
def record_quality_performance(
    payload: QualityPerformanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_performance_write_access(current_user)
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
    sync_overall_score(db, record)

    refresh_vendor_ranking(db, payload.vendor_id)
    db.commit()
    db.refresh(record)
    refresh_after_performance_write(payload.vendor_id, db)

    return {
        "vendor_id": payload.vendor_id,
        "purchase_order_id": payload.purchase_order_id,
        "overall_score": record.overall_performance_score,
        "performance_status": record.performance_status,
        "notes": record.notes,
        "evaluation_date": record.evaluation_date,
    }


@router.get("/quality/{vendor_id}", response_model=list[QualityPerformanceOut])
def list_quality_performance(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_vendor_performance_access(vendor_id, current_user, db)
    return (
        db.query(ProductQualityEvaluation)
        .filter(ProductQualityEvaluation.vendor_id == vendor_id)
        .order_by(ProductQualityEvaluation.inspection_date.desc())
        .all()
    )


@router.post("/communication", response_model=PerformanceActionResponse)
def record_communication_performance(
    payload: CommunicationPerformanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_performance_write_access(current_user)
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
    sync_overall_score(db, record)

    refresh_vendor_ranking(db, payload.vendor_id)
    db.commit()
    db.refresh(record)
    refresh_after_performance_write(payload.vendor_id, db)

    return {
        "vendor_id": payload.vendor_id,
        "purchase_order_id": payload.purchase_order_id,
        "overall_score": record.overall_performance_score,
        "performance_status": record.performance_status,
        "notes": record.notes,
        "evaluation_date": record.evaluation_date,
    }


@router.get("/communication/{vendor_id}", response_model=list[CommunicationPerformanceOut])
def list_communication_logs(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_vendor_performance_access(vendor_id, current_user, db)
    return (
        db.query(CommunicationLog)
        .filter(CommunicationLog.vendor_id == vendor_id)
        .order_by(CommunicationLog.message_sent_time.desc())
        .all()
    )


@router.post("/service-rating", response_model=PerformanceActionResponse)
def record_service_rating(
    payload: ServiceRatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_performance_write_access(current_user)
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
    sync_overall_score(db, record)

    refresh_vendor_ranking(db, payload.vendor_id)
    db.commit()
    db.refresh(record)
    refresh_after_performance_write(payload.vendor_id, db)

    return {
        "vendor_id": payload.vendor_id,
        "purchase_order_id": payload.purchase_order_id,
        "overall_score": record.overall_performance_score,
        "performance_status": record.performance_status,
        "notes": record.notes,
        "evaluation_date": record.evaluation_date,
    }


@router.get("/service-rating/{vendor_id}", response_model=list[ServiceRatingOut])
def list_service_ratings(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_vendor_performance_access(vendor_id, current_user, db)
    return (
        db.query(ServiceRating)
        .filter(ServiceRating.vendor_id == vendor_id)
        .order_by(ServiceRating.id.desc())
        .all()
    )


@router.get("/vendors/{vendor_id}/issues", response_model=list[VendorIssueOut])
def list_vendor_issues(
    vendor_id: int,
    include_closed: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Read the persisted issue/complaint history for one vendor."""
    _require_vendor_performance_access(vendor_id, current_user, db)
    return [
        _issue_response(issue)
        for issue in vendor_issue_service.list_vendor_issues(
            db, vendor_id, include_closed=include_closed
        )
    ]


@router.post("/vendors/{vendor_id}/issues", response_model=VendorIssueOut, status_code=201)
def create_issue(
    vendor_id: int,
    payload: VendorIssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Log an operational issue or complaint without manufacturing performance data."""
    _require_performance_write_access(current_user)
    if not db.query(Vendor).filter(Vendor.id == vendor_id).first():
        raise HTTPException(status_code=404, detail="Vendor not found")
    try:
        issue = vendor_issue_service.create_vendor_issue(
            db,
            vendor_id=vendor_id,
            purchase_order_id=payload.purchase_order_id,
            issue_category=payload.category.strip(),
            severity=payload.severity,
            description=payload.description.strip(),
            status="Open",
            reported_by=current_user.id,
            assigned_to=payload.assigned_to,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return _issue_response(issue)


@router.patch("/vendors/{vendor_id}/issues/{issue_id}", response_model=VendorIssueOut)
def update_issue(
    vendor_id: int,
    issue_id: int,
    payload: VendorIssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update issue workflow metadata; resolving requires resolution notes."""
    _require_performance_write_access(current_user)
    issue = vendor_issue_service.get_vendor_issue(db, issue_id)
    if not issue or issue.vendor_id != vendor_id:
        raise HTTPException(status_code=404, detail="Vendor issue not found")
    changes = payload.model_dump(exclude_unset=True)
    if "category" in changes:
        changes["issue_category"] = changes.pop("category")
    try:
        updated = vendor_issue_service.update_vendor_issue(
            db, issue_id, updated_by=current_user.id, **changes
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not updated:
        raise HTTPException(status_code=404, detail="Vendor issue not found")
    return _issue_response(updated)


@router.post("/vendors/{vendor_id}/issues/{issue_id}/resolve", response_model=VendorIssueOut)
def resolve_issue(
    vendor_id: int,
    issue_id: int,
    payload: VendorIssueResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Provide an explicit resolve action for clients that do not use PATCH."""
    _require_performance_write_access(current_user)
    issue = vendor_issue_service.get_vendor_issue(db, issue_id)
    if not issue or issue.vendor_id != vendor_id:
        raise HTTPException(status_code=404, detail="Vendor issue not found")
    try:
        resolved = vendor_issue_service.resolve_vendor_issue(
            db,
            issue_id,
            resolution_notes=payload.resolution_notes,
            resolved_by=current_user.id,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not resolved:
        raise HTTPException(status_code=404, detail="Vendor issue not found")
    return _issue_response(resolved)


@router.get(
    "/history/{vendor_id}",
    response_model=list[PerformanceRecordOut] | PerformanceHistoryWithIssuesOut,
)
def performance_history(
    vendor_id: int,
    include_issues: bool = Query(False, alias="includeIssues"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return legacy record history, or a record-and-issue history envelope.

    Leaving ``includeIssues`` false preserves Module 4 consumers which expect a
    list.  New issue-aware screens can opt into the enriched response without a
    second round trip.
    """
    _require_vendor_performance_access(vendor_id, current_user, db)
    records = (
        db.query(PerformanceRecord)
        .filter(PerformanceRecord.vendor_id == vendor_id)
        .order_by(PerformanceRecord.evaluation_date.desc())
        .all()
    )
    performance_records = [performance_record_response(record) for record in records]
    if include_issues:
        return {
            "performance_history": performance_records,
            "issue_history": vendor_issue_service.vendor_issue_performance_history(db, vendor_id),
        }
    return performance_records


@router.get("/rankings", response_model=VendorRankingOut)
def vendor_rankings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_performance_read_access(current_user)
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
    _require_performance_write_access(current_user)
    if not can_user_recalculate_vendor_ranking(current_user.role):
        raise HTTPException(
            status_code=403,
            detail="Only Administrator or Procurement Manager can recalculate vendor rankings",
        )
    records = db.query(PerformanceRecord).all()
    for record in records:
        refresh_vendor_ranking(db, record.vendor_id)
    db.commit()
    return vendor_rankings(db, current_user)


@router.get("/{vendor_id}", response_model=PerformanceRecordOut)
def get_vendor_performance(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_vendor_performance_access(vendor_id, current_user, db)
    record = (
        db.query(PerformanceRecord)
        .filter(PerformanceRecord.vendor_id == vendor_id)
        .order_by(PerformanceRecord.evaluation_date.desc())
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Performance record not found")
    return performance_record_response(record)
