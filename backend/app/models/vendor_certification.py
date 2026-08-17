from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class VendorCertification(Base):
    __tablename__ = "vendor_certifications"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)

    certification_name = Column(String(255), nullable=False)  # ISO 9001, ISO 27001, Medical Cert, etc.
    certificate_number = Column(String(100), nullable=True)
    issuing_authority = Column(String(255), nullable=True)

    issue_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True, index=True)

    file_name = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)

    status = Column(String(50), default="Active", index=True)  # Active, Expiring Soon, Expired, Revoked
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
