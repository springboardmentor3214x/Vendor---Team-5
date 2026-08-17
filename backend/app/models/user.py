from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Allowed values: Administrator, Procurement Manager, Supply Chain Manager,
    # Vendor, Finance Officer, Auditor
    role = Column(String(50), default="Vendor")

    mobile_number = Column(String(20), nullable=True)
    employee_id = Column(String(50), nullable=True)
    company_name = Column(String(255), nullable=True)
    profile_picture_url = Column(String(500), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)