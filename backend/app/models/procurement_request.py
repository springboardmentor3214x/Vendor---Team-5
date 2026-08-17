from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ProcurementRequest(Base):
    __tablename__ = "procurement_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    project_name = Column(String(255), nullable=True)
    item_description = Column(String(500), nullable=False)
    
    product_name = Column(String(255), nullable=False)
    product_category = Column(String(100), nullable=False)
    quantity = Column(Integer, default=1)
    unit_of_measurement = Column(String(50), nullable=True)
    estimated_budget = Column(Float, nullable=False, default=0.0)
    required_delivery_date = Column(DateTime, nullable=False)
    priority = Column(String(50), nullable=False, default="Medium", index=True)
    business_justification = Column(String(1000), nullable=False)
    additional_remarks = Column(String(1000), nullable=True)

    requested_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    request_date = Column(DateTime, default=datetime.utcnow)

    approval_status = Column(String(50), default="Pending", index=True)
    # Allowed: Draft, Pending, Approved, Rejected, Cancelled, Sent Back
    approval_remarks = Column(String(1000), nullable=True)

    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    approved_date = Column(DateTime, nullable=True)

    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True, index=True)
    vendor = relationship("Vendor")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)