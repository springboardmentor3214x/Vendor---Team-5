from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, normalize_user_role
from app.core.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationListOut, NotificationMarkAllReadOut, NotificationOut, NotificationReadOut,
    NotificationSummaryOut, NotificationUnreadCountOut,
)
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _out(notification: Notification) -> NotificationOut:
    return NotificationOut(
        id=notification.id, title=notification.title, message=notification.message,
        type=getattr(notification, "type", "INFO"), notification_type=getattr(notification, "notification_type", None),
        related_module=getattr(notification, "related_module", None), related_record_id=getattr(notification, "related_record_id", None),
        priority=getattr(notification, "priority", None), delivery_method=getattr(notification, "delivery_method", None),
        is_read=getattr(notification, "is_read", False), read_at=getattr(notification, "read_at", None),
        link=getattr(notification, "link", None), created_at=getattr(notification, "created_at", None),
    )


@router.get("/", response_model=NotificationListOut)
def list_notifications(
    module: str | None = None, priority: str | None = None, is_read: bool | None = Query(default=None, alias="isRead"),
    notification_type: str | None = Query(default=None, alias="notificationType"), date_from: datetime | None = Query(default=None, alias="dateFrom"),
    date_to: datetime | None = Query(default=None, alias="dateTo"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    filters = {"module": module, "priority": priority, "is_read": is_read, "notification_type": notification_type,
               "date_from": date_from, "date_to": date_to}
    items = notification_service.get_user_notifications(db, current_user.id, filters)
    unread = notification_service.get_unread_notifications(db, current_user.id)
    return NotificationListOut(items=[_out(item) for item in items], total=len(items), unread_count=len(unread))


@router.get("/unread-count", response_model=NotificationUnreadCountOut)
def get_unread_notification_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return NotificationUnreadCountOut(unread_count=len(notification_service.get_unread_notifications(db, current_user.id)))


@router.get("/summary", response_model=NotificationSummaryOut)
def get_notification_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = notification_service.get_notification_summary(db, current_user.id)
    return NotificationSummaryOut(
        total_notifications=result["total_notifications"], unread_count=result["unread_count"],
        high_priority_count=result["high_priority_count"], recent_notifications=[_out(item) for item in result["recent_notifications"]],
    )


@router.patch("/read-all", response_model=NotificationMarkAllReadOut)
def mark_all_notifications_as_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    updated = notification_service.mark_all_notifications_read(db, current_user.id)
    return NotificationMarkAllReadOut(message="Notifications marked as read", updated_count=updated)


@router.get("/{notification_id}", response_model=NotificationOut)
def get_notification(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return _out(item)


@router.patch("/{notification_id}/read", response_model=NotificationReadOut)
def mark_notification_as_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = notification_service.mark_notification_as_read(db, notification_id, current_user.id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return NotificationReadOut(message="Notification marked as read", notification=_out(item))


@router.post("/scan")
def scan_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if normalize_user_role(current_user) not in {"Administrator", "Procurement Manager"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return notification_service.scan_for_pending_notifications(db)
