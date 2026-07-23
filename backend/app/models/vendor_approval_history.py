from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class VendorApprovalHistory(Base):
    __tablename__ = "vendor_approval_history"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(50), nullable=False)  # e.g., Approve, Reject, Suspend, Activate
    remarks = Column(String(1000), nullable=True)
    action_date = Column(DateTime, default=datetime.utcnow, index=True)
