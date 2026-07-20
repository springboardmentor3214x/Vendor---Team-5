from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    module = Column(String(100), nullable=False)      # e.g. "Vendor", "Procurement"
    action = Column(String(100), nullable=False)      # e.g. "Created", "Approved", "Updated"
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)