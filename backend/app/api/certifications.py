from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.api.auth import get_current_user, normalize_user_role
from app.schemas.certification import CertificationCreate, CertificationUpdate, CertificationOut
from app.services import certification_service
from app.api.reliability_refresh import refresh_after_compliance_update

router = APIRouter(prefix="/certifications", tags=["Certifications"])


@router.post("/", response_model=CertificationOut, status_code=status.HTTP_201_CREATED)
def add_certification(payload: CertificationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Admins, Procurement Managers can upload certifications, Vendors can upload their own
    if normalize_user_role(current_user) == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or payload.vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only add certifications for yourself")
    elif normalize_user_role(current_user) not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    certification = certification_service.add_certification(db, payload)
    refresh_after_compliance_update(certification.vendor_id, db)
    return certification


@router.patch("/{certification_id}", response_model=CertificationOut)
def update_certification(certification_id: int, payload: CertificationUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cert = db.query(certification_service.Certification).filter(certification_service.Certification.id == certification_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")

    if normalize_user_role(current_user) == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or cert.vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif normalize_user_role(current_user) not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    updated_certification = certification_service.update_certification(db, certification_id, payload)
    refresh_after_compliance_update(updated_certification.vendor_id, db)
    return updated_certification


@router.delete("/{certification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certification(certification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cert = db.query(certification_service.Certification).filter(certification_service.Certification.id == certification_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")

    if normalize_user_role(current_user) == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or cert.vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif normalize_user_role(current_user) not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    vendor_id = cert.vendor_id
    certification_service.delete_certification(db, certification_id)
    refresh_after_compliance_update(vendor_id, db)


@router.get("/vendor/{vendor_id}", response_model=List[CertificationOut])
def get_vendor_certifications(vendor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if normalize_user_role(current_user) == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return certification_service.get_vendor_certifications(db, vendor_id)
