from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class ContractDocument(Base):
    __tablename__ = "contract_documents"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)

    document_type = Column(String(100), nullable=False)
    # Allowed: Signed Agreement, Amendment, Renewal Notice, Compliance Certificate, Other

    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)

    uploaded_at = Column(DateTime, default=datetime.utcnow)