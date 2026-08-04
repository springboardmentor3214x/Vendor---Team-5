from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.notification import (
    NotificationListOut,
    NotificationOut,
    NotificationReadOut,
    NotificationUnreadCountOut,
    BackgroundCheckResultOut,
)
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _notification_out(notification) -> NotificationOut:
    return NotificationOut(
        id=notification.id,
        user_id=getattr(notification, "user_id", None),
        vendor_id=getattr(notification, "vendor_id", None),
        contract_id=getattr(notification, "contract_id", None),
        purchase_order_id=getattr(notification, "purchase_order_id", None),
        procurement_request_id=getattr(notification, "procurement_request_id", None),
        title=notification.title,
        message=notification.message,
        type=getattr(notification, "notification_type", getattr(notification, "type", "INFO")),
        notification_type=getattr(notification, "notification_type", getattr(notification, "type", "INFO")),
        related_module=getattr(notification, "related_module", None),
        related_record_id=getattr(notification, "related_record_id", None),
        priority=getattr(notification, "priority", "MEDIUM"),
        delivery_method=getattr(notification, "delivery_method", "IN_APP"),
        is_read=getattr(notification, "is_read", False),
        read_at=getattr(notification, "read_at", None),
        link=getattr(notification, "link", None),
        created_at=getattr(notification, "created_at", None),
    )


@router.get("", response_model=NotificationListOut)
@router.get("/", response_model=NotificationListOut)
def list_notifications(
    module: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    is_read: Optional[bool] = Query(None, alias="isRead"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch notifications for current user with optional module, priority, and read status filters."""
    notifications = notification_service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        module=module,
        priority=priority,
        is_read=is_read,
    )
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
    """Get count of unread notifications for current user."""
    unread_notifications = notification_service.get_unread_notifications(db, current_user.id)
    return NotificationUnreadCountOut(unread_count=len(unread_notifications))


@router.patch("/{notification_id}/read", response_model=NotificationReadOut)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark single notification as read."""
    notification = notification_service.mark_notification_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return NotificationReadOut(
        message="Notification marked as read",
        notification=_notification_out(notification),
    )


@router.post("/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all unread notifications for current user as read."""
    count = notification_service.mark_all_user_notifications_as_read(db, current_user.id)
    return {
        "status": "success",
        "message": f"Marked {count} notifications as read",
        "marked_count": count,
    }


@router.post("/trigger-background-checks", response_model=BackgroundCheckResultOut)
def trigger_background_checks_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger background check scanners for contract expiry, delivery delays, and compliance alerts."""
    return notification_service.execute_all_background_notification_checks(db=db)
