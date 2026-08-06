from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommunicationCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    # senderId is accepted only for legacy-client compatibility and is ignored.
    sender_id: int | None = Field(default=None, alias="senderId")
    receiver_id: int | None = Field(default=None, alias="receiverId")
    vendor_id: int | None = Field(default=None, alias="vendorId")
    procurement_request_id: int | None = Field(default=None, alias="procurementRequestId")
    purchase_order_id: int | None = Field(default=None, alias="purchaseOrderId")
    contract_id: int | None = Field(default=None, alias="contractId")
    invoice_id: int | None = Field(default=None, alias="invoiceId")
    discussion_id: int | None = Field(default=None, alias="discussionId")
    subject: str | None = None
    message: str = Field(min_length=1, max_length=5000)
    message_type: str | None = Field(default="DIRECT", alias="messageType")


class CommunicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    sender_id: int = Field(alias="senderId")
    receiver_id: int | None = Field(default=None, alias="receiverId")
    vendor_id: int | None = Field(default=None, alias="vendorId")
    procurement_request_id: int | None = Field(default=None, alias="procurementRequestId")
    purchase_order_id: int | None = Field(default=None, alias="purchaseOrderId")
    contract_id: int | None = Field(default=None, alias="contractId")
    invoice_id: int | None = Field(default=None, alias="invoiceId")
    discussion_id: int | None = Field(default=None, alias="discussionId")
    subject: str | None = None
    message: str
    message_type: str | None = Field(default=None, alias="messageType")
    is_read: bool = Field(default=False, alias="isRead")
    read_at: datetime | None = Field(default=None, alias="readAt")
    created_at: datetime = Field(alias="createdAt")


class DiscussionCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    title: str = Field(min_length=1, max_length=255)
    participant_ids: list[int] = Field(default_factory=list, alias="participantIds")
    vendor_id: int | None = Field(default=None, alias="vendorId")
    procurement_request_id: int | None = Field(default=None, alias="procurementRequestId")
    purchase_order_id: int | None = Field(default=None, alias="purchaseOrderId")
    contract_id: int | None = Field(default=None, alias="contractId")
    invoice_id: int | None = Field(default=None, alias="invoiceId")
    status: str | None = "OPEN"


class DiscussionParticipantCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    user_id: int = Field(alias="userId", gt=0)


class DiscussionParticipantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    discussion_id: int = Field(alias="discussionId")
    user_id: int = Field(alias="userId")
    joined_at: datetime = Field(alias="joinedAt")


class DiscussionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    title: str
    created_by_id: int = Field(alias="createdById")
    vendor_id: int | None = Field(default=None, alias="vendorId")
    procurement_request_id: int | None = Field(default=None, alias="procurementRequestId")
    purchase_order_id: int | None = Field(default=None, alias="purchaseOrderId")
    contract_id: int | None = Field(default=None, alias="contractId")
    invoice_id: int | None = Field(default=None, alias="invoiceId")
    status: str | None = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")


class DiscussionDetailOut(DiscussionOut):
    participants: list[DiscussionParticipantOut] = Field(default_factory=list)
    messages: list[CommunicationResponse] = Field(default_factory=list)


class CommunicationFileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    filename: str
    file_type: str | None = Field(default=None, alias="fileType")
    file_size: int | None = Field(default=None, alias="fileSize")
    uploaded_by_id: int = Field(alias="uploadedById")
    message_id: int | None = Field(default=None, alias="messageId")
    discussion_id: int | None = Field(default=None, alias="discussionId")
    vendor_id: int | None = Field(default=None, alias="vendorId")
    procurement_request_id: int | None = Field(default=None, alias="procurementRequestId")
    purchase_order_id: int | None = Field(default=None, alias="purchaseOrderId")
    contract_id: int | None = Field(default=None, alias="contractId")
    created_at: datetime = Field(alias="createdAt")


class ActivityLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    user_id: int | None = Field(default=None, alias="userId")
    module: str
    action: str
    description: str | None = None
    related_entity_type: str | None = Field(default=None, alias="relatedEntityType")
    related_entity_id: int | None = Field(default=None, alias="relatedEntityId")
    ip_address: str | None = Field(default=None, alias="ipAddress")
    created_at: datetime = Field(alias="createdAt")
