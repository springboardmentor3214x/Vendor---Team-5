from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorOut, VendorUpdate
from app.services.vendor_service import (
    approve_vendor, reject_vendor, validate_unique_vendor_fields
)

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.post("/", response_model=VendorOut)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db)):
    email_exists = db.query(Vendor).filter(Vendor.email == payload.email).first() is not None
    gst_exists = db.query(Vendor).filter(Vendor.gst_number == payload.gst_number).first() is not None
    pan_exists = db.query(Vendor).filter(Vendor.pan_number == payload.pan_number).first() is not None
    reg_exists = db.query(Vendor).filter(
        Vendor.company_registration_number == payload.company_registration_number
    ).first() is not None

    if not validate_unique_vendor_fields(email_exists, gst_exists, pan_exists, reg_exists):
        raise HTTPException(status_code=400, detail="Duplicate email, GST, PAN or registration number")

    vendor = Vendor(**payload.model_dump())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.get("/", response_model=list[VendorOut])
def list_vendors(status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Vendor)
    if status:
        query = query.filter(Vendor.vendor_status == status)
    return query.all()


@router.get("/{vendor_id}", response_model=VendorOut)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.patch("/{vendor_id}", response_model=VendorOut)
def update_vendor(vendor_id: int, payload: VendorUpdate, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vendor, field, value)

    db.commit()
    db.refresh(vendor)
    return vendor


@router.patch("/{vendor_id}/approve", response_model=VendorOut)
def approve_vendor_route(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    try:
        vendor.approval_status = approve_vendor(vendor.approval_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    db.refresh(vendor)
    return vendor


@router.patch("/{vendor_id}/reject", response_model=VendorOut)
def reject_vendor_route(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    try:
        vendor.approval_status = reject_vendor(vendor.approval_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    db.refresh(vendor)
    return vendor