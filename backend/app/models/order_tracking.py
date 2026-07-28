from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class OrderTracking(Base):
    __tablename__ = "order_tracking"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), unique=True, nullable=False, index=True)
    
    dispatch_date = Column(DateTime, nullable=True)
    expected_delivery_date = Column(DateTime, nullable=False)
    actual_delivery_date = Column(DateTime, nullable=True)
    
    delivery_status = Column(String(50), default="Awaiting Shipment", index=True)
    # Allowed: Awaiting Shipment, In Transit, Delivered, Delayed, Completed
    
    delay_days = Column(Integer, default=0)
    remarks = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    purchase_order = relationship("PurchaseOrder")
