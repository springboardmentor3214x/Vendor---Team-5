from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class ContractRenewal(Base):
    __tablename__ = "contract_renewals"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True)

    renewal_date = Column(DateTime, default=datetime.utcnow)
    new_end_date = Column(DateTime, nullable=False)
    renewal_value = Column(Float, default=0.0)
    remarks = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
