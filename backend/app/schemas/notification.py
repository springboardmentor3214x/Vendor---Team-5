from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class NotificationOut(BaseModel):
    """API representation for Module 9 notification items."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    id: int
    user_id: Optional[int] = Field(default=None, alias="userId")
    vendor_id: Optional[int] = Field(default=None, alias="vendorId")
    contract_id: Optional[int] = Field(default=None, alias="contractId")
    purchase_order_id: Optional[int] = Field(default=None, alias="purchaseOrderId")
    procurement_request_id: Optional[int] = Field(default=None, alias="procurementRequestId")

    title: str
    message: str
    type: str = Field(default="INFO")  # Legacy alias
    notification_type: str = Field(default="INFO", alias="notificationType")

    related_module: Optional[str] = Field(default=None, alias="relatedModule")
    related_record_id: Optional[int] = Field(default=None, alias="relatedRecordId")

    priority: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    delivery_method: str = Field(default="IN_APP", alias="deliveryMethod")  # IN_APP, EMAIL, SMS, ALL

    is_read: bool = Field(default=False, alias="isRead")
    read_at: Optional[datetime] = Field(default=None, alias="readAt")
    link: Optional[str] = None
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")


class NotificationListOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: List[NotificationOut]
    total: int
    unread_count: int = Field(alias="unreadCount")


class NotificationReadOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: str
    notification: NotificationOut


class NotificationUnreadCountOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    unread_count: int = Field(alias="unreadCount")


class BackgroundCheckResultOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: str
    contract_expiry_alerts_generated: int = Field(alias="contractExpiryAlertsGenerated")
    delivery_delay_alerts_generated: int = Field(alias="deliveryDelayAlertsGenerated")
    compliance_expiry_alerts_generated: int = Field(alias="complianceExpiryAlertsGenerated")
