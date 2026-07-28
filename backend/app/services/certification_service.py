from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.models.certification import Certification
from app.schemas.certification import CertificationCreate, CertificationUpdate


def add_certification(db: Session, payload: CertificationCreate) -> Certification:
    cert = Certification(**payload.model_dump())
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


def update_certification(db: Session, certification_id: int, payload: CertificationUpdate) -> Optional[Certification]:
    cert = db.query(Certification).filter(Certification.id == certification_id).first()
    if not cert:
        return None
    
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cert, key, value)
        
    cert.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(cert)
    return cert


def delete_certification(db: Session, certification_id: int) -> bool:
    cert = db.query(Certification).filter(Certification.id == certification_id).first()
    if not cert:
        return False
    db.delete(cert)
    db.commit()
    return True


def get_vendor_certifications(db: Session, vendor_id: int) -> List[Certification]:
    return db.query(Certification).filter(Certification.vendor_id == vendor_id).all()
