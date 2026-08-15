from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
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
    file_size = Column(Integer, nullable=True)
    content_type = Column(String(100), nullable=True)  # e.g. application/pdf, image/png

    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    version = Column(Integer, default=1, nullable=False)
    is_current = Column(Boolean, default=True, nullable=False)
    replaced_document_id = Column(Integer, ForeignKey("vendor_documents.id"), nullable=True)
    replaced_at = Column(DateTime, nullable=True)
    replaced_by = Column(Integer, ForeignKey("users.id"), nullable=True)