from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from datetime import datetime
from app.core.database import Base


class ContractRenewal(Base):
    __tablename__ = "contract_renewals"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False, index=True)

    previous_end_date = Column(DateTime, nullable=True)
    new_end_date = Column(DateTime, nullable=False)

    renewal_date = Column(DateTime, default=datetime.utcnow)
    renewed_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    renewal_notes = Column(Text, nullable=True)
    remarks = Column(String(500), nullable=True)
    revised_contract_value = Column(Float, nullable=True)
    renewal_value = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
