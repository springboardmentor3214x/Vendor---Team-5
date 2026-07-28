from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base  # will connect once Pranjal pushes database.py


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)

    contract_number = Column(String(100), unique=True, nullable=False, index=True)
    contract_title = Column(String(255), nullable=False)
    contract_type = Column(String(100), nullable=True)  # e.g. Supply, Service, NDA
    procurement_category = Column(String(100), nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)

    contract_value = Column(Float, default=0.0)
    payment_terms = Column(String(255), nullable=True)
    sla = Column(String(500), nullable=True)
    warranty_details = Column(String(500), nullable=True)
    responsible_manager = Column(String(255), nullable=True)
    document_url = Column(String(500), nullable=True)

    status = Column(String(50), default="Draft")  # Draft, Active, Expired, Renewed, Terminated
    compliance_verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # vendor = relationship("Vendor", back_populates="contracts")
