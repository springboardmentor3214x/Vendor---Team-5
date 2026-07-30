from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.dashboard import Module6DashboardOut
from app.services.dashboard_service import get_module6_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

_DASHBOARD_ROLES = {
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
    if _role_name(current_user) not in _DASHBOARD_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return get_module6_dashboard_summary(db, user_id=current_user.id)
