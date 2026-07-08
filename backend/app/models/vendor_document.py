from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class VendorDocument(Base):
    __tablename__ = "vendor_documents"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)

    document_type = Column(String(100), nullable=False)
    # Allowed: GST Certificate, PAN Card, Company Registration Certificate,
    # ISO Certificate, Other Supporting Document

    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # storage location/URL

    uploaded_at = Column(DateTime, default=datetime.utcnow)