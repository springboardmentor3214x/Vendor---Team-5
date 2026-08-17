from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from datetime import datetime
from app.core.database import Base


class Communication(Base):
    __tablename__ = "communications"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True, index=True)
    procurement_request_id = Column(Integer, ForeignKey("procurement_requests.id"), nullable=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True, index=True)
    discussion_id = Column(Integer, ForeignKey("discussions.id"), nullable=True, index=True)

    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    message_type = Column(String(50), default="DIRECT", index=True)
    # Types: DIRECT, DISCUSSION, QUOTATION, DELIVERY, PAYMENT, DOCUMENTATION, CONTRACT, SHIPMENT, PRODUCT

    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)