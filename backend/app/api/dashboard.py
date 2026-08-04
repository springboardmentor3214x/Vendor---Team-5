from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.vendor import Vendor
from app.schemas.dashboard import (
    Module6DashboardOut,
    ProcurementDashboardOut,
    PersonalizedVendorDashboardOut,
    AdminDashboardOut,
    CostAnalysisOut,
    ChartDataResponse,
)
from app.services.dashboard_service import (
    get_module6_dashboard_summary,
    get_procurement_manager_dashboard_summary,
    get_personalized_vendor_dashboard,
    get_admin_dashboard_summary,
    get_procurement_cost_analysis,
    get_chart_datasets_summary,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

_MANAGEMENT_ROLES = {
    "Administrator",
    "Procurement Manager",
    "Supply Chain Manager",
    "Finance Officer",
    "Auditor",
}


def _role_name(current_user: User) -> str | None:
    role = getattr(current_user, "role", None)
    return getattr(role, "name", role)


@router.get("", response_model=Module6DashboardOut)
def get_module6_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Module 6 backward compatible dashboard metrics."""
    return get_module6_dashboard_summary(db, user_id=current_user.id)


@router.get("/procurement", response_model=ProcurementDashboardOut)
def get_procurement_dashboard(
    start_date: Optional[date] = Query(None, alias="startDate"),
    end_date: Optional[date] = Query(None, alias="endDate"),
    category_id: Optional[int] = Query(None, alias="categoryId"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Procurement Manager Dashboard with request status, delivery metrics, department breakdown, and top vendors."""
    return get_procurement_manager_dashboard_summary(
        db=db,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
    )


@router.get("/vendor", response_model=PersonalizedVendorDashboardOut)
def get_vendor_dashboard(
    vendor_id: Optional[int] = Query(None, alias="vendorId"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Personalized Vendor Dashboard metrics (scoped to logged in vendor or requested vendor ID)."""
    target_vendor_id = vendor_id
    if not target_vendor_id:
        # Resolve vendor linked to current user
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if vendor:
            target_vendor_id = vendor.id
        else:
            first_vendor = db.query(Vendor).first()
            target_vendor_id = first_vendor.id if first_vendor else 1

    return get_personalized_vendor_dashboard(
        db=db,
        vendor_id=target_vendor_id,
        user_id=current_user.id,
    )


@router.get("/admin", response_model=AdminDashboardOut)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin Dashboard overview for system statistics, total users, vendors, and application health."""
    if _role_name(current_user) and _role_name(current_user) not in ["Administrator", "Procurement Manager", "Auditor"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin dashboard access restricted")

    return get_admin_dashboard_summary(db=db)


@router.get("/cost-analysis", response_model=CostAnalysisOut)
def get_cost_analysis_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Procurement Cost Analysis breakdown by department, vendor category, and monthly spending trend."""
    return get_procurement_cost_analysis(db=db)


@router.get("/charts", response_model=ChartDataResponse)
def get_chart_datasets_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Chart data visualization datasets (Bar, Line, Pie, Doughnut)."""
    return get_chart_datasets_summary(db=db)
