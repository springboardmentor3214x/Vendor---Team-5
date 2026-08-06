from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    module = Column(String(100), nullable=False, index=True)      # e.g. "Communication", "Vendor", "Procurement"
    action = Column(String(100), nullable=False, index=True)      # e.g. "MESSAGE_SENT", "DISCUSSION_CREATED", "FILE_UPLOADED"
    description = Column(String(500), nullable=True)

    related_entity_type = Column(String(100), nullable=True, index=True)  # e.g. "Vendor", "PurchaseOrder", "Contract"
    related_entity_id = Column(Integer, nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)