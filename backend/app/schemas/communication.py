from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


# --- Message Schemas ---
class CommunicationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")
    sender_id: Optional[int] = Field(default=None, alias="senderId")
    receiver_id: Optional[int] = Field(default=None, alias="receiverId")
    vendor_id: Optional[int] = Field(default=None, alias="vendorId")
    procurement_request_id: Optional[int] = Field(default=None, alias="procurementRequestId")
    purchase_order_id: Optional[int] = Field(default=None, alias="purchaseOrderId")
    contract_id: Optional[int] = Field(default=None, alias="contractId")
    invoice_id: Optional[int] = Field(default=None, alias="invoiceId")
    discussion_id: Optional[int] = Field(default=None, alias="discussionId")

    subject: Optional[str] = None
    message: str
    message_type: Optional[str] = Field(default="DIRECT", alias="messageType")


class CommunicationCreate(CommunicationBase):
    pass


class CommunicationResponse(CommunicationBase):
    id: int
    is_read: bool = Field(default=False, alias="isRead")
    read_at: Optional[datetime] = Field(default=None, alias="readAt")
    created_at: datetime = Field(alias="createdAt")


# --- Discussion Schemas ---
class DiscussionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")
    title: str
    vendor_id: Optional[int] = Field(default=None, alias="vendorId")
    procurement_request_id: Optional[int] = Field(default=None, alias="procurementRequestId")
    purchase_order_id: Optional[int] = Field(default=None, alias="purchaseOrderId")
    contract_id: Optional[int] = Field(default=None, alias="contractId")
    invoice_id: Optional[int] = Field(default=None, alias="invoiceId")


class DiscussionCreate(DiscussionBase):
    participant_user_ids: Optional[List[int]] = Field(default_factory=list, alias="participantUserIds")
    initial_message: Optional[str] = Field(default=None, alias="initialMessage")


class DiscussionResponse(DiscussionBase):
    id: int
    created_by_id: int = Field(alias="createdById")
    status: str
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    messages: Optional[List[CommunicationResponse]] = Field(default_factory=list)
    participant_count: Optional[int] = Field(default=0, alias="participantCount")


# --- File Attachment Schemas ---
class CommunicationFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")
    id: int
    filename: str
    file_path: str = Field(alias="filePath")
    file_type: Optional[str] = Field(default=None, alias="fileType")
    file_size: Optional[int] = Field(default=None, alias="fileSize")
    uploaded_by_id: int = Field(alias="uploadedById")
    message_id: Optional[int] = Field(default=None, alias="messageId")
    discussion_id: Optional[int] = Field(default=None, alias="discussionId")
    vendor_id: Optional[int] = Field(default=None, alias="vendorId")
    procurement_request_id: Optional[int] = Field(default=None, alias="procurementRequestId")
    purchase_order_id: Optional[int] = Field(default=None, alias="purchaseOrderId")
    contract_id: Optional[int] = Field(default=None, alias="contractId")
    created_at: datetime = Field(alias="createdAt")


# --- Activity Log Schemas ---
class ActivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")
    id: int
    user_id: Optional[int] = Field(default=None, alias="userId")
    module: str
    action: str
    description: Optional[str] = None
    related_entity_type: Optional[str] = Field(default=None, alias="relatedEntityType")
    related_entity_id: Optional[int] = Field(default=None, alias="relatedEntityId")
    ip_address: Optional[str] = Field(default=None, alias="ipAddress")
    created_at: datetime = Field(alias="createdAt")