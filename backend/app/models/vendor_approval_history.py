from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class VendorApprovalHistory(Base):
    __tablename__ = "vendor_approval_history"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)

    action = Column(String(50), nullable=False)
    # Allowed: Approved, Rejected, Pending, Suspended

    remarks = Column(String(1000), nullable=True)

    acted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acted_at = Column(DateTime, default=datetime.utcnow)