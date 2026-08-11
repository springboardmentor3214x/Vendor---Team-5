from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class ProcurementRiskLevel(Base):
    __tablename__ = "procurement_risk_levels"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), unique=True, nullable=False, index=True)

    risk_level = Column(String(50), default="Medium Risk", index=True)
    # Allowed: Low Risk, Medium Risk, High Risk

    risk_reason = Column(String(500), nullable=True)
    requires_warning = Column(Integer, default=0)  # 0 = False, 1 = True (boolean-like flag)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)