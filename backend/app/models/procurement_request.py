from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class ProcurementRequest(Base):
    __tablename__ = "procurement_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String(100), unique=True, nullable=False)

    department = Column(String(100), nullable=False)
    item_description = Column(String(500), nullable=False)
    quantity = Column(Integer, default=1)

    requested_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    request_date = Column(DateTime, default=datetime.utcnow)

    approval_status = Column(String(50), default="Pending", index=True)
    # Allowed: Pending, Approved, Rejected, Cancelled

    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
