from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ProcurementApproval(Base):
    __tablename__ = "procurement_approvals"

    id = Column(Integer, primary_key=True, index=True)
    procurement_request_id = Column(Integer, ForeignKey("procurement_requests.id"), nullable=False, index=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False)  # e.g., Approved, Rejected, Sent Back
    remarks = Column(String(1000), nullable=True)
    approved_at = Column(DateTime, default=datetime.utcnow)

    procurement_request = relationship("ProcurementRequest")
    approver = relationship("User")
