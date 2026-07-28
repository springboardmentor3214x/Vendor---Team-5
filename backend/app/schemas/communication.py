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
    pass


class CommunicationResponse(CommunicationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True