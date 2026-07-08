from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime
from app.core.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Info
    company_name = Column(String(255), nullable=False)
    vendor_category = Column(String(100), nullable=False)
    # Allowed: Raw Material Suppliers, Equipment Vendors, IT Vendors,
    # Service Providers, Logistics Partners, Maintenance Vendors

    contact_person_name = Column(String(255), nullable=False)
    designation = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=False)
    alternate_phone = Column(String(20), nullable=True)

    # Legal / Registration
    gst_number = Column(String(50), nullable=True)
    pan_number = Column(String(50), nullable=True)
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
    vendor_status = Column(String(50), default="Pending")
    # Allowed: Active, Pending, Inactive, Suspended, Rejected
    approval_status = Column(String(50), default="Pending")
    # Allowed: Pending, Approved, Rejected

    reliability_score = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)