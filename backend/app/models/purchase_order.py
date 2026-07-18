from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    procurement_request_id = Column(Integer, ForeignKey("procurement_requests.id"), unique=True, nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)

    po_number = Column(String(100), unique=True, nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)

    expected_delivery_date = Column(DateTime, nullable=True)
    actual_delivery_date = Column(DateTime, nullable=True)
    payment_terms = Column(String(255), nullable=True)

    po_status = Column(String(50), default="Draft", index=True)
    # Allowed: Draft, Issued, Delivered, Cancelled

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)