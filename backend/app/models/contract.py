from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from datetime import datetime
from app.core.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    contract_number = Column(String(100), unique=True, index=True, nullable=True)
    contract_title = Column(String(255), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    procurement_request_id = Column(Integer, ForeignKey("procurement_requests.id"), nullable=True, index=True)

    contract_type = Column(String(100), nullable=True)  # e.g. Supply, Service, NDA, Maintenance
    procurement_category = Column(String(100), nullable=True)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True, index=True)

    contract_value = Column(Float, default=0.0)
    payment_terms = Column(String(255), nullable=True)
    sla_details = Column(Text, nullable=True)
    warranty_details = Column(Text, nullable=True)

    responsible_manager_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    status = Column(String(50), default="Draft", index=True)  # Draft, Active, Expired, Renewed, Terminated
    compliance_verified = Column(Boolean, default=False)
    signed_document_path = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)