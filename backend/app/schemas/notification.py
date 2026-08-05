from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationOut(BaseModel):
    """DB-backed in-app notification returned to the authenticated recipient."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    title: str
    message: str
    type: str = "INFO"
    notification_type: str | None = Field(default=None, alias="notificationType")
    related_module: str | None = Field(default=None, alias="relatedModule")
    related_record_id: int | None = Field(default=None, alias="relatedRecordId")
    priority: str | None = None
    delivery_method: str | None = Field(default=None, alias="deliveryMethod")
    is_read: bool = Field(default=False, alias="isRead")
    read_at: datetime | None = Field(default=None, alias="readAt")
    link: str | None = None
    created_at: datetime | None = Field(default=None, alias="createdAt")


class NotificationListOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    items: list[NotificationOut]
    total: int
    unread_count: int = Field(alias="unreadCount")


class NotificationReadOut(BaseModel):
    message: str
    notification: NotificationOut


class NotificationUnreadCountOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    unread_count: int = Field(alias="unreadCount")


class NotificationMarkAllReadOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    message: str
    updated_count: int = Field(alias="updatedCount")


class NotificationSummaryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    total_notifications: int = Field(alias="totalNotifications")
    unread_count: int = Field(alias="unreadCount")
    high_priority_count: int = Field(alias="highPriorityCount")
    recent_notifications: list[NotificationOut] = Field(alias="recentNotifications")
