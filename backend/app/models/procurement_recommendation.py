from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class ProcurementRecommendation(Base):
    __tablename__ = "procurement_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("vendor_categories.id"), nullable=True, index=True)

    recommendation_score = Column(Float, default=0.0)
    # Legacy reliability recommendation columns remain in deployed databases and
    # are consumed by the reliability recommendations API.
    reliability_score = Column(Float, default=0.0)
    risk_level = Column(String(50), default="Medium Risk", index=True)
    recommendation_status = Column(String(50), default="Recommended", index=True)
    # Allowed: Recommended, Not Recommended, Caution

    reason = Column(String(500), nullable=True)

    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
