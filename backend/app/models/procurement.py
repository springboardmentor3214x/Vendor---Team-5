# DEPRECATED: This model is obsolete. 
# It was split into ProcurementRequest and PurchaseOrder in migrations.
# Kept here only for backward-compatibility to prevent import errors.
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ProcurementOrder(Base):
    __tablename__ = "procurement_orders"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)

    order_number = Column(String(100), unique=True, nullable=False)
    item_description = Column(String(500), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)

    order_date = Column(DateTime, default=datetime.utcnow)
    expected_delivery_date = Column(DateTime, nullable=True)
    actual_delivery_date = Column(DateTime, nullable=True)

    status = Column(String(50), default="pending")  # pending, approved, delivered, cancelled

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # vendor = relationship("Vendor")
    # contract = relationship("Contract")