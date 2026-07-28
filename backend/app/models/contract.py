from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base  # will connect once Pranjal pushes database.py


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)

    contract_title = Column(String(255), nullable=False)
    contract_type = Column(String(100), nullable=True)  # e.g. Supply, Service, NDA
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

    contract_value = Column(Float, default=0.0)
    status = Column(String(50), default="active")  # active, expired, terminated
    compliance_verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # vendor = relationship("Vendor", back_populates="contracts")
