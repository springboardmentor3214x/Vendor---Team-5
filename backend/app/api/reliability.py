from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.vendor import Vendor
from app.models.vendor_category import VendorCategory
from app.models.reliability import VendorReliability, PerformanceTrend, ProcurementRecommendation
from app.schemas.reliability import (
    VendorReliabilityOut,
    PerformanceTrendOut,
    ProcurementRecommendationOut,
    ReliabilityRecalculationResult,
    ReliabilityRiskItem,
    ReliabilityDashboardOut,
    VendorRankItem
)
from app.services.reliability_service import recalculate_vendor_reliability
from app.utils.constants import ROLE_ADMIN, ROLE_PROCUREMENT_MANAGER, ROLE_VENDOR

router = APIRouter(prefix="/reliability", tags=["Reliability"])


def check_manager_or_admin(current_user: User):
    """
    Ensure the user is an Admin, Procurement Manager, or Supply Chain Manager.
    """
    if current_user.role not in [ROLE_ADMIN, ROLE_PROCUREMENT_MANAGER, "Supply Chain Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: requires administrator or procurement manager role."
        )


def check_vendor_access(vendor_id: int, current_user: User, db: Session):
    """
    Allow manager/admin, or allow the vendor themselves if email matches.
    """
    if current_user.role in [ROLE_ADMIN, ROLE_PROCUREMENT_MANAGER, "Supply Chain Manager"]:
        return
    if current_user.role == ROLE_VENDOR:
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if vendor and vendor.email == current_user.email:
            return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied: you do not have permission to view this vendor's data."
    )


def _reliability_ranking_query(db: Session):
    """Return Module 5 ranking data from persisted reliability scores only."""
    return (
        db.query(
            VendorReliability.vendor_id,
            Vendor.company_name,
            VendorCategory.name,
            VendorReliability.reliability_score,
            VendorReliability.risk_level,
        )
        .join(Vendor, Vendor.id == VendorReliability.vendor_id)
        .outerjoin(VendorCategory, VendorCategory.id == Vendor.category_id)
    )


@router.get("/dashboard", response_model=ReliabilityDashboardOut)
def get_reliability_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_manager_or_admin(current_user)

    # Calculate average reliability score
    avg_score = db.query(func.avg(VendorReliability.reliability_score)).scalar() or 0.0

    # Count risk levels
    high_rel_count = db.query(func.count(VendorReliability.id)).filter(
        VendorReliability.reliability_score >= 80
    ).scalar() or 0

    med_rel_count = db.query(func.count(VendorReliability.id)).filter(
        VendorReliability.reliability_score >= 50,
        VendorReliability.reliability_score < 80
    ).scalar() or 0

    high_risk_count = db.query(func.count(VendorReliability.id)).filter(
        VendorReliability.reliability_score < 50
    ).scalar() or 0

    # Module 5 rankings are dynamic and derived from reliability_score, not
    # the separate Module 4 VendorRanking performance table.
    top_rankings = (
        _reliability_ranking_query(db)
        .order_by(
            VendorReliability.reliability_score.desc(),
            VendorReliability.vendor_id.asc(),
        )
        .limit(5)
        .all()
    )

    top_ranked = [
        VendorRankItem(
            vendor_id=item[0],
            vendor_name=item[1],
            vendor_category=item[2],
            reliability_score=item[3],
            risk_level=item[4],
            rank_position=position,
        )
        for position, item in enumerate(top_rankings, start=1)
    ]

    # Total vendors evaluated is the count of rows in vendor_reliability table
    total_vendors = db.query(func.count(VendorReliability.id)).scalar() or 0

    return ReliabilityDashboardOut(
        total_vendors_evaluated=total_vendors,
        average_reliability_score=round(avg_score, 2),
        high_reliability_count=high_rel_count,
        medium_reliability_count=med_rel_count,
        high_risk_count=high_risk_count,
        top_ranked_vendors=top_ranked
    )


@router.get("/details/{vendor_id}", response_model=VendorReliabilityOut)
def get_reliability_details(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_vendor_access(vendor_id, current_user, db)

    rel = db.query(VendorReliability).filter(VendorReliability.vendor_id == vendor_id).first()
    if not rel:
        # Trigger an initial calculation if not found
        try:
            rel = recalculate_vendor_reliability(vendor_id, db)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    return rel


@router.post("/recalculate/{vendor_id}", response_model=VendorReliabilityOut)
def trigger_recalculate(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_manager_or_admin(current_user)

    try:
        rel = recalculate_vendor_reliability(vendor_id, db)
        return rel
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/recalculate-all", response_model=ReliabilityRecalculationResult)
def trigger_recalculate_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_manager_or_admin(current_user)

    vendors = db.query(Vendor).all()
    count = 0
    for vendor in vendors:
        try:
            recalculate_vendor_reliability(vendor.id, db)
            count += 1
        except Exception:
            continue

    return {
        "message": f"Successfully recalculated reliability score for {count} vendors.",
        "recalculatedVendors": count,
    }


@router.get("/rankings", response_model=List[VendorRankItem])
def get_supplier_rankings(
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_manager_or_admin(current_user)

    query = _reliability_ranking_query(db)

    if category_id is not None:
        query = query.filter(Vendor.category_id == category_id)

    rankings_data = query.order_by(
        VendorReliability.reliability_score.desc(),
        VendorReliability.vendor_id.asc(),
    ).all()

    return [
        VendorRankItem(
            vendor_id=item[0],
            vendor_name=item[1],
            vendor_category=item[2],
            reliability_score=item[3],
            risk_level=item[4],
            rank_position=position,
        )
        for position, item in enumerate(rankings_data, start=1)
    ]


@router.get("/risk-levels", response_model=List[ReliabilityRiskItem])
def get_procurement_risk_levels(
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_manager_or_admin(current_user)

    query = _reliability_ranking_query(db)

    if risk_level is not None:
        query = query.filter(VendorReliability.risk_level == risk_level)

    data = query.all()

    result = []
    for item in data:
        result.append(
            ReliabilityRiskItem(
                vendor_id=item[0],
                vendor_name=item[1],
                vendor_category=item[2],
                reliability_score=item[3],
                risk_level=item[4],
            )
        )

    return result


@router.get("/trends/{vendor_id}", response_model=List[PerformanceTrendOut])
def get_vendor_trends(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_vendor_access(vendor_id, current_user, db)

    trends = (
        db.query(PerformanceTrend)
        .filter(PerformanceTrend.vendor_id == vendor_id)
        .order_by(PerformanceTrend.year.asc(), PerformanceTrend.month.asc())
        .all()
    )

    return trends


@router.get("/recommendations", response_model=List[ProcurementRecommendationOut])
def get_procurement_recommendations(
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_manager_or_admin(current_user)

    query = (
        db.query(
            ProcurementRecommendation.id,
            ProcurementRecommendation.vendor_id,
            Vendor.company_name,
            VendorCategory.name,
            ProcurementRecommendation.reliability_score,
            ProcurementRecommendation.risk_level,
            ProcurementRecommendation.recommendation_status,
            ProcurementRecommendation.reason,
            ProcurementRecommendation.updated_at
        )
        .join(Vendor, Vendor.id == ProcurementRecommendation.vendor_id)
        .outerjoin(VendorCategory, VendorCategory.id == Vendor.category_id)
    )

    if category_id is not None:
        query = query.filter(Vendor.category_id == category_id)

    # Return recommendations sorted by reliability score descending
    recommendations_data = query.order_by(ProcurementRecommendation.reliability_score.desc()).all()

    result = []
    for item in recommendations_data:
        result.append(
            ProcurementRecommendationOut(
                id=item[0],
                vendor_id=item[1],
                vendor_name=item[2],
                vendor_category=item[3],
                reliability_score=item[4],
                risk_level=item[5],
                recommendation_status=item[6],
                reason=item[7],
                updated_at=item[8]
            )
        )

    return result
