from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Info
    company_name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("vendor_categories.id"), nullable=False, index=True)
    category = relationship("VendorCategory", back_populates="vendors")

    contact_person_name = Column(String(255), nullable=False)
    designation = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=False)
    alternate_phone = Column(String(20), nullable=True)

    # Legal / Registration
    gst_number = Column(String(50), unique=True, nullable=True, index=True)
    pan_number = Column(String(50), unique=True, nullable=True, index=True)
    company_registration_number = Column(String(100), nullable=True)

    # Address
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    pincode = Column(String(20), nullable=True)

    website = Column(String(255), nullable=True)
    description = Column(String(1000), nullable=True)

    # Banking
    bank_account_number = Column(String(50), nullable=True)
    ifsc_code = Column(String(20), nullable=True)
    payment_terms = Column(String(255), nullable=True)

    # Status
    vendor_status = Column(String(50), default="Pending", index=True)
    # Allowed: Active, Pending, Inactive, Suspended, Rejected
    approval_status = Column(String(50), default="Pending", index=True)
    # Allowed: Pending, Approved, Rejected

    reliability_score = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    contacts = relationship("VendorContact", back_populates="vendor")