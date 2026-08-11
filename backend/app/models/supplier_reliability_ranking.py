from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class SupplierReliabilityRanking(Base):
    __tablename__ = "supplier_reliability_ranking"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), unique=True, nullable=False, index=True)

    reliability_score = Column(Float, default=0.0)
    rank_position = Column(Integer, nullable=True, index=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)