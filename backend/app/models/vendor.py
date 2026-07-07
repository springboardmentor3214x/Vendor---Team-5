from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base  # adjust import once Pranjal's core/database.py exists


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)  # e.g. Raw Materials, IT Services

    reliability_score = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (uncomment once related models exist)
    # contracts = relationship("Contract", back_populates="vendor")
    # performance_records = relationship("PerformanceRecord", back_populates="vendor")