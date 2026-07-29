from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from app.core.database import Base


class ReportLog(Base):
    __tablename__ = "report_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    report_type = Column(String(100), nullable=False)
    # Allowed: Vendor Performance Summary, Procurement Overview, Compliance Audit, Contract Renewal Report

    file_format = Column(String(20), nullable=False)  # PDF, EXCEL, CSV
    file_path = Column(String(500), nullable=True)
    parameters = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
