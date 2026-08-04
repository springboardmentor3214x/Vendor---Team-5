from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.activity_log import ActivityLog


def log_activity(
    db: Session,
    user_id: Optional[int],
    module: str,
    action: str,
    description: Optional[str] = None,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[int] = None,
    ip_address: Optional[str] = None
) -> ActivityLog:
    """Utility to record system action in activity_logs table for audit trail."""
    activity = ActivityLog(
        user_id=user_id,
        module=module,
        action=action,
        description=description,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        ip_address=ip_address
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def query_activity_logs(
    db: Session,
    module: Optional[str] = None,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[ActivityLog]:
    """Retrieve filtered activity logs for compliance and audit trail."""
    query = db.query(ActivityLog)
    if module:
        query = query.filter(ActivityLog.module.ilike(f"%{module}%"))
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    if action:
        query = query.filter(ActivityLog.action.ilike(f"%{action}%"))

    return query.order_by(ActivityLog.created_at.desc()).offset(offset).limit(limit).all()
