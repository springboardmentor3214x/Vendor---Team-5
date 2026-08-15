from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class VendorIssue(Base):
    __tablename__ = "vendor_issues"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True, index=True)

    issue_category = Column(String(100), nullable=False, index=True)
    # E.g. Quality Defect, Late Delivery, Billing Discrepancy, Communication Failure, Compliance Violation, Other

    severity = Column(String(50), nullable=False, default="Medium", index=True)
    # E.g. Low, Medium, High, Critical

    description = Column(String(1000), nullable=False)

    status = Column(String(50), nullable=False, default="Open", index=True)
    # E.g. Open, In Progress, Resolved, Escalated, Closed

    reported_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    reported_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    resolution_notes = Column(String(1000), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    resolved_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
