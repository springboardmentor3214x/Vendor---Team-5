from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.api.auth import get_current_user
from app.schemas.compliance import ComplianceRecordCreate, ComplianceRecordOut, ComplianceVerify
from app.services import compliance_service

router = APIRouter(prefix="/compliance", tags=["Compliance"])


@router.post("/verify", response_model=ComplianceRecordOut)
def verify_compliance_record(payload: ComplianceRecordCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Only Admin and Procurement Manager can verify/add compliance records
    if current_user.role.name not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    record = compliance_service.create_compliance_record(db, payload)
    # Perform immediate verification setup
    return compliance_service.verify_compliance(
        db, 
        compliance_id=record.id, 
        status=payload.status, 
        verified_by=current_user.id, 
        remarks=payload.remarks
    )


@router.patch("/{compliance_id}/status", response_model=ComplianceRecordOut)
def update_compliance_status(compliance_id: int, payload: ComplianceVerify, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return compliance_service.verify_compliance(
        db,
        compliance_id=compliance_id,
        status=payload.status,
        verified_by=current_user.id,
        remarks=payload.remarks
    )


@router.get("/vendor/{vendor_id}", response_model=List[ComplianceRecordOut])
def get_vendor_compliance_history(vendor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.name == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return compliance_service.get_vendor_compliance_history(db, vendor_id)
