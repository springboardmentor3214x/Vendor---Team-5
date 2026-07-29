from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from app.core.database import Base


class ComplianceRecord(Base):
    __tablename__ = "compliance_records"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True, index=True)

    compliance_type = Column(String(100), nullable=False)
    # Allowed: Government Licenses, GST Registration, Safety Regulations, Quality Standards,
    # Industry Regulations, Environmental Compliance, Cybersecurity Standards

    compliance_status = Column(String(50), default="Pending Verification", index=True)
    # Allowed: Compliant, Pending Verification, Non-Compliant, Expired

    verification_date = Column(DateTime, nullable=True)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
