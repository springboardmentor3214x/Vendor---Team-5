from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class VendorReliabilityScore(Base):
    __tablename__ = "vendor_reliability_scores"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), unique=True, nullable=False, index=True)

    reliability_score = Column(Float, default=0.0)

    delivery_factor = Column(Float, default=0.0)
    quality_factor = Column(Float, default=0.0)
    communication_factor = Column(Float, default=0.0)
    compliance_factor = Column(Float, default=0.0)
    purchase_history_factor = Column(Float, default=0.0)
    issue_resolution_factor = Column(Float, default=0.0)

    risk_level = Column(String(50), default="Medium Risk", index=True)
    # Allowed: Low Risk, Medium Risk, High Risk

    last_calculated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)