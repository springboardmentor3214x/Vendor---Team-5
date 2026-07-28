from datetime import datetime

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/notifications", tags=["Notifications"])

notifications_store = [
    {"id": 1, "title": "Contract expiring soon", "message": "Vendor contract will expire within 30 days.", "type": "warning", "is_read": False, "created_at": datetime.utcnow()},
    {"id": 2, "title": "Performance updated", "message": "Vendor performance score has been recalculated.", "type": "info", "is_read": False, "created_at": datetime.utcnow()},
]


@router.get("/")
def list_notifications():
    unread_count = sum(1 for item in notifications_store if not item["is_read"])
    return {"items": notifications_store, "total": len(notifications_store), "unread_count": unread_count}


@router.patch("/{notification_id}/read")
def mark_notification_as_read(notification_id: int):
    for item in notifications_store:
        if item["id"] == notification_id:
            item["is_read"] = True
            return {"message": "Notification marked as read", "notification": item}
    raise HTTPException(status_code=404, detail="Notification not found")
