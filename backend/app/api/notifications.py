from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.notification import (
    NotificationListOut,
    NotificationOut,
    NotificationReadOut,
    NotificationUnreadCountOut,
)
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def _notification_out(notification) -> NotificationOut:
    return NotificationOut(
        id=notification.id,
        title=notification.title,
        message=notification.message,
        type=getattr(notification, "notification_type", getattr(notification, "type", "info")),
        is_read=getattr(notification, "is_read", False),
        created_at=getattr(notification, "created_at", None),
    )


@router.get("/", response_model=NotificationListOut)
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notifications = notification_service.get_user_notifications(db, current_user.id)
    unread_notifications = notification_service.get_unread_notifications(db, current_user.id)
    return NotificationListOut(
        items=[_notification_out(item) for item in notifications],
        total=len(notifications),
        unread_count=len(unread_notifications),
    )


@router.get("/unread-count", response_model=NotificationUnreadCountOut)
def get_unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    unread_notifications = notification_service.get_unread_notifications(db, current_user.id)
    return NotificationUnreadCountOut(unread_count=len(unread_notifications))


@router.patch("/{notification_id}/read", response_model=NotificationReadOut)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = notification_service.mark_notification_as_read(
        db,
        notification_id,
        current_user.id,
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationReadOut(
        message="Notification marked as read",
        notification=_notification_out(notification),
    )
