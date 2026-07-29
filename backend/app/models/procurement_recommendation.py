from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class ProcurementRecommendation(Base):
    __tablename__ = "procurement_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("vendor_categories.id"), nullable=True, index=True)

    recommendation_score = Column(Float, default=0.0)
    recommendation_status = Column(String(50), default="Recommended", index=True)
    # Allowed: Recommended, Not Recommended, Caution

    reason = Column(String(500), nullable=True)

    generated_at = Column(DateTime, default=datetime.utcnow, index=True)