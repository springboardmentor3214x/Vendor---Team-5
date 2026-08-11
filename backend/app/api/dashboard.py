from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, normalize_user_role
from app.core.database import get_db
from app.models.user import User
from app.models.vendor import Vendor
from app.schemas.dashboard import DashboardDataOut, Module6DashboardOut
from app.services.dashboard_service import (
    get_active_purchase_orders_summary, get_admin_dashboard_summary, get_dashboard_chart_data,
    get_delivery_status_dashboard, get_module6_dashboard_summary, get_procurement_cost_analysis,
    get_procurement_dashboard_summary, get_procurement_overview, get_vendor_dashboard_summary,
    get_vendor_performance_dashboard,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

_DASHBOARD_ROLES = {"Administrator", "Procurement Manager", "Supply Chain Manager", "Finance Officer", "Auditor"}
_MANAGEMENT_ROLES = {"Administrator", "Procurement Manager", "Supply Chain Manager", "Finance Officer", "Auditor"}
_ANALYTICS_ROLES = {"Administrator", "Procurement Manager", "Supply Chain Manager", "Finance Officer", "Auditor"}


def _role(current_user: User) -> str | None:
    return normalize_user_role(current_user)


def _require(current_user: User, roles: set[str]) -> None:
    if _role(current_user) not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


def _filters(department: str | None, vendor_id: int | None) -> dict[str, object]:
    return {key: value for key, value in {"department": department, "vendor_id": vendor_id}.items() if value is not None}


def _vendor_for_user(db: Session, current_user: User) -> Vendor:
    vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No vendor profile is linked to the current account")
    return vendor


@router.get("", response_model=Module6DashboardOut)
def get_module6_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user, _DASHBOARD_ROLES)
    return get_module6_dashboard_summary(db, user_id=current_user.id)


@router.get("/procurement-manager", response_model=DashboardDataOut)
def procurement_manager_dashboard(department: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user, {"Administrator", "Procurement Manager", "Supply Chain Manager"})
    return {"data": get_procurement_dashboard_summary(db, _filters(department, None))}


@router.get("/procurement-statistics", response_model=DashboardDataOut)
def procurement_statistics(department: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user, _ANALYTICS_ROLES)
    return {"data": get_procurement_overview(db, _filters(department, None))}


@router.get("/purchase-orders/active", response_model=DashboardDataOut)
def active_purchase_orders(department: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user, _MANAGEMENT_ROLES)
    return {"data": {"items": get_active_purchase_orders_summary(db, _filters(department, None))}}


@router.get("/vendor-performance", response_model=DashboardDataOut)
def vendor_performance_dashboard(vendor_id: int | None = Query(default=None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if _role(current_user) == "Vendor":
        vendor_id = _vendor_for_user(db, current_user).id
    else:
        _require(current_user, _ANALYTICS_ROLES)
    return {"data": get_vendor_performance_dashboard(db, _filters(None, vendor_id))}


@router.get("/cost-analysis", response_model=DashboardDataOut)
def procurement_cost_analysis(department: str | None = None, vendor_id: int | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if _role(current_user) == "Vendor":
        vendor_id = _vendor_for_user(db, current_user).id
    else:
        _require(current_user, _ANALYTICS_ROLES)
    return {"data": get_procurement_cost_analysis(db, _filters(department, vendor_id))}


@router.get("/delivery-status", response_model=DashboardDataOut)
def delivery_status(department: str | None = None, vendor_id: int | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if _role(current_user) == "Vendor":
        vendor_id = _vendor_for_user(db, current_user).id
    else:
        _require(current_user, _MANAGEMENT_ROLES)
    return {"data": get_delivery_status_dashboard(db, _filters(department, vendor_id))}


@router.get("/charts", response_model=DashboardDataOut)
def dashboard_charts(department: str | None = None, vendor_id: int | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if _role(current_user) == "Vendor":
        vendor_id = _vendor_for_user(db, current_user).id
    else:
        _require(current_user, _ANALYTICS_ROLES)
    return {"data": get_dashboard_chart_data(db, _filters(department, vendor_id))}


@router.get("/vendor", response_model=DashboardDataOut)
def vendor_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if _role(current_user) != "Vendor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This dashboard is only available to vendor accounts")
    vendor = _vendor_for_user(db, current_user)
    return {"data": get_vendor_dashboard_summary(db, vendor.id)}


@router.get("/admin", response_model=DashboardDataOut)
def admin_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require(current_user, {"Administrator"})
    return {"data": get_admin_dashboard_summary(db)}
