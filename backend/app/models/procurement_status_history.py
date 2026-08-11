from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ProcurementStatusHistory(Base):
    __tablename__ = "procurement_status_history"

    id = Column(Integer, primary_key=True, index=True)
    procurement_request_id = Column(Integer, ForeignKey("procurement_requests.id"), nullable=False, index=True)
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    remarks = Column(String(1000), nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow, index=True)

    procurement_request = relationship("ProcurementRequest")
    user = relationship("User", foreign_keys=[changed_by])
