from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class VendorReliability(Base):
    __tablename__ = "vendor_reliability"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), unique=True, nullable=False, index=True)

    delivery_score = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    compliance_score = Column(Float, default=0.0)
    issue_resolution_score = Column(Float, default=0.0)

    reliability_score = Column(Float, default=0.0)
    risk_level = Column(String(50), default="Medium", index=True)
    recommendation = Column(String(500), nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PerformanceTrend(Base):
    __tablename__ = "performance_trends"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1 to 12

    reliability_score = Column(Float, default=0.0)
    delivery_score = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    compliance_score = Column(Float, default=0.0)
    issue_resolution_score = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)


class ProcurementRecommendation(Base):
    __tablename__ = "procurement_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), unique=True, nullable=False, index=True)

    reliability_score = Column(Float, default=0.0)
    risk_level = Column(String(50), default="Medium", index=True)
    recommendation_status = Column(String(100), default="Monitor")  # Recommended, Monitor, Not Recommended
    reason = Column(String(500), nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
