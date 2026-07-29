from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    """API representation for the current notification placeholder store."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    message: str
    type: str = "info"
    is_read: bool = False
    created_at: datetime | None = None


class NotificationListOut(BaseModel):
    items: list[NotificationOut]
    total: int
    unread_count: int


class NotificationReadOut(BaseModel):
    message: str
    notification: NotificationOut


class NotificationUnreadCountOut(BaseModel):
    unread_count: int
