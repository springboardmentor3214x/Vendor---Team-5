from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CommunicationBase(BaseModel):
    sender_id: int
    vendor_id: Optional[int] = None
    procurement_request_id: Optional[int] = None
    subject: Optional[str] = None
    message: str


class CommunicationCreate(CommunicationBase):
    pass


class CommunicationResponse(CommunicationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True