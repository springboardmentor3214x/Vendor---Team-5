from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from app.core.database import Base


class InvoiceDocument(Base):
    __tablename__ = "invoice_documents"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)

    document_type = Column(String(100), nullable=False, default="Invoice Document")
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    content_type = Column(String(100), nullable=True)

    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    version = Column(Integer, default=1, nullable=False)
    is_current = Column(Boolean, default=True, nullable=False)
    replaced_document_id = Column(Integer, ForeignKey("invoice_documents.id"), nullable=True)
    replaced_at = Column(DateTime, nullable=True)
    replaced_by = Column(Integer, ForeignKey("users.id"), nullable=True)
