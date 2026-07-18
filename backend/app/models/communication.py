from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from app.core.database import Base


class Communication(Base):
    __tablename__ = "communications"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True, index=True)
    procurement_request_id = Column(Integer, ForeignKey("procurement_requests.id"), nullable=True, index=True)

    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)