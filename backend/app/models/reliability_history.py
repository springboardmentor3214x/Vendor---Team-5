from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class ReliabilityHistory(Base):
    __tablename__ = "reliability_history"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)

    reliability_score = Column(Float, nullable=True)
    delivery_trend = Column(String(50), nullable=True)      # Improving / Declining / Stable
    quality_trend = Column(String(50), nullable=True)
    communication_trend = Column(String(50), nullable=True)
    compliance_trend = Column(String(50), nullable=True)
    issue_resolution_trend = Column(String(50), nullable=True)

    recorded_month = Column(String(20), nullable=True)  # e.g. "2026-07"
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)