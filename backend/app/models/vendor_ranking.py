from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class VendorRanking(Base):
    __tablename__ = "vendor_rankings"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), unique=True, nullable=False, index=True)

    overall_performance_score = Column(Float, default=0.0)
    delivery_score = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    service_rating_score = Column(Float, default=0.0)

    rank_position = Column(Integer, nullable=True, index=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)