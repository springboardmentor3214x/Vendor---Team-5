from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, normalize_user_role
from app.core.database import get_db
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.schemas.communication import ActivityLogOut
from app.services.activity_log_service import list_activity_logs

router = APIRouter(prefix="/activity-logs", tags=["Activity Logs"])
_AUDIT_ROLES = {"Administrator", "Procurement Manager", "Supply Chain Manager", "Auditor"}


def _require_audit_access(current_user: User) -> None:
    if normalize_user_role(current_user) not in _AUDIT_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.get("/", response_model=list[ActivityLogOut])
def get_activity_logs(user_id: int | None = Query(default=None), module: str | None = None, action: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require_audit_access(current_user)
    return list_activity_logs(db, {"user_id": user_id, "module": module, "action": action})


@router.get("/{log_id}", response_model=ActivityLogOut)
def get_activity_log(log_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require_audit_access(current_user)
    item = db.query(ActivityLog).filter(ActivityLog.id == log_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity log not found")
    return item
