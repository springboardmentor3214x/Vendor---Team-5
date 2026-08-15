from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from datetime import datetime
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True, index=True)
    procurement_request_id = Column(Integer, ForeignKey("procurement_requests.id"), nullable=True, index=True)

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="INFO", index=True)  # Legacy compatibility alias
    notification_type = Column(String(50), default="INFO", index=True)
    # Types: VENDOR_APPROVAL, VENDOR_REJECTION, PROCUREMENT_ALERT, DELIVERY_DELAY, CONTRACT_EXPIRY, COMPLIANCE_ALERT, INVOICE_UPDATE, INFO, WARNING

    related_module = Column(String(100), nullable=True, index=True)  # Procurement, Vendor, Contracts, Compliance, Communication
    related_record_id = Column(Integer, nullable=True, index=True)

    priority = Column(String(20), default="MEDIUM", index=True)  # HIGH, MEDIUM, LOW
    delivery_method = Column(String(20), default="IN_APP")  # IN_APP, EMAIL, SMS, ALL

    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime, nullable=True)
    link = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
