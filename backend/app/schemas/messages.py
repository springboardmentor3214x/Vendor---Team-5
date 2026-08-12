"""Schemas for the dedicated Module 7 direct-message workspace."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.message import RelatedEntityType


class MessageCreate(BaseModel):
    """A direct message.  Sender identity always comes from the JWT."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    receiver_id: int = Field(alias="receiverId", gt=0)
    content: str = Field(min_length=1, max_length=10_000)
    related_entity_type: RelatedEntityType = Field(
        default=RelatedEntityType.NONE,
        alias="relatedEntityType",
    )
    related_entity_id: Optional[int] = Field(default=None, alias="relatedEntityId", gt=0)


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    sender_id: int = Field(alias="senderId")
    receiver_id: int = Field(alias="receiverId")
    content: str
    related_entity_type: RelatedEntityType = Field(alias="relatedEntityType")
    related_entity_id: Optional[int] = Field(default=None, alias="relatedEntityId")
    is_read: bool = Field(alias="isRead")
    created_at: datetime = Field(alias="createdAt")
    read_at: Optional[datetime] = Field(default=None, alias="readAt")


class ConversationSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    counterpart_user_id: int = Field(alias="counterpartUserId")
    counterpart_name: Optional[str] = Field(default=None, alias="counterpartName")
    counterpart_email: Optional[str] = Field(default=None, alias="counterpartEmail")
    last_message_content: str = Field(alias="lastMessageContent")
    last_message_at: datetime = Field(alias="lastMessageAt")
    unread_count: int = Field(alias="unreadCount")
    related_entity_type: Optional[RelatedEntityType] = Field(default=None, alias="relatedEntityType")
    related_entity_id: Optional[int] = Field(default=None, alias="relatedEntityId")


class MessageContact(BaseModel):
    """A real, context-scoped recipient that can be selected for direct messaging."""

    model_config = ConfigDict(populate_by_name=True)

    user_id: int = Field(alias="userId")
    full_name: str = Field(alias="fullName")
    email: str
    role: Optional[str] = None


class UnreadMessageCountOut(BaseModel):
    unread: int
