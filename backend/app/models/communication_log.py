from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class CommunicationLog(Base):
    __tablename__ = "communication_logs"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)

    message_sent_time = Column(DateTime, nullable=True)
    vendor_response_time = Column(DateTime, nullable=True)
    response_duration_minutes = Column(Integer, nullable=True)
    # calculated: (vendor_response_time - message_sent_time) in minutes

    communication_status = Column(String(50), nullable=True, index=True)
    # Allowed: Pending, Responded, No Response, Escalated

    remarks = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)