from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class CommunicationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")
    sender_id: int = Field(alias="senderId")
    vendor_id: Optional[int] = Field(default=None, alias="vendorId")
    procurement_request_id: Optional[int] = Field(default=None, alias="procurementRequestId")
    subject: Optional[str] = None
    message: str


class CommunicationCreate(CommunicationBase):
    # The API always derives the persisted sender from the JWT user.  Keep the
    # legacy input optional so existing clients that send senderId do not break.
    sender_id: Optional[int] = Field(default=None, alias="senderId")


class CommunicationResponse(CommunicationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
