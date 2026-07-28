from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.models.compliance import ComplianceRecord
from app.schemas.compliance import ComplianceRecordCreate


def create_compliance_record(db: Session, payload: ComplianceRecordCreate) -> ComplianceRecord:
    record = ComplianceRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def verify_compliance(db: Session, compliance_id: int, status: str, verified_by: int, remarks: Optional[str] = None) -> Optional[ComplianceRecord]:
    record = db.query(ComplianceRecord).filter(ComplianceRecord.id == compliance_id).first()
    if not record:
        return None
    record.status = status
    record.verified_by = verified_by
    record.verification_date = datetime.utcnow()
    if remarks:
        record.remarks = remarks
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


def get_vendor_compliance_history(db: Session, vendor_id: int) -> List[ComplianceRecord]:
    return db.query(ComplianceRecord).filter(ComplianceRecord.vendor_id == vendor_id).all()


def update_compliance_status(db: Session, compliance_id: int, status: str) -> Optional[ComplianceRecord]:
    record = db.query(ComplianceRecord).filter(ComplianceRecord.id == compliance_id).first()
    if not record:
        return None
    record.status = status
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record
