from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.api.auth import get_current_user
from app.schemas.certification import CertificationCreate, CertificationUpdate, CertificationOut
from app.services import certification_service

router = APIRouter(prefix="/certifications", tags=["Certifications"])


@router.post("/", response_model=CertificationOut, status_code=status.HTTP_201_CREATED)
def add_certification(payload: CertificationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Admins, Procurement Managers can upload certifications, Vendors can upload their own
    if current_user.role.name == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or payload.vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only add certifications for yourself")
    elif current_user.role.name not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return certification_service.add_certification(db, payload)


@router.patch("/{certification_id}", response_model=CertificationOut)
def update_certification(certification_id: int, payload: CertificationUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cert = db.query(certification_service.Certification).filter(certification_service.Certification.id == certification_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")

    if current_user.role.name == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or cert.vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif current_user.role.name not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return certification_service.update_certification(db, certification_id, payload)


@router.delete("/{certification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certification(certification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cert = db.query(certification_service.Certification).filter(certification_service.Certification.id == certification_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")

    if current_user.role.name == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or cert.vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif current_user.role.name not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    certification_service.delete_certification(db, certification_id)


@router.get("/vendor/{vendor_id}", response_model=List[CertificationOut])
def get_vendor_certifications(vendor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return certification_service.get_vendor_certifications(db, vendor_id)
