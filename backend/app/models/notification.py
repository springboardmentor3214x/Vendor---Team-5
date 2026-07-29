from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from datetime import datetime
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True, index=True)

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="INFO", index=True)
    # Allowed: CONTRACT_EXPIRY, CERTIFICATION_EXPIRY, COMPLIANCE_ALERT, INFO, WARNING

    is_read = Column(Boolean, default=False, index=True)
    link = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
