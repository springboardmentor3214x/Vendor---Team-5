from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base  # will connect once Pranjal pushes database.py


class PerformanceRecord(Base):
    __tablename__ = "performance_records"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)

    on_time_delivery = Column(Float, default=0.0)      # % or score
    quality_rating = Column(Float, default=0.0)        # e.g. out of 5 or 10
    communication_score = Column(Float, default=0.0)
    compliance_score = Column(Float, default=0.0)

    overall_score = Column(Float, default=0.0)         # computed by Sonali's scoring logic
    risk_level = Column(String(50), default="low")     # low, medium, high

    evaluation_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String(1000), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # vendor = relationship("Vendor")
    # procurement_order = relationship("ProcurementOrder")
    # purchase_order = relationship("PurchaseOrder")
