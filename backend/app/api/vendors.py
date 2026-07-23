from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.vendor import Vendor
from app.schemas.vendor import (
    VendorApprovalAction,
    VendorDocumentOut,
    VendorOut,
    VendorUpdate,
    VendorCreate,
)
from app.services.vendor_service import (
    approve_vendor,
    reject_vendor,
    validate_unique_vendor_fields,
)

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.post("/", response_model=VendorOut, status_code=status.HTTP_201_CREATED)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db)):
    email_exists = db.query(Vendor).filter(Vendor.email == payload.email).first() is not None
    gst_exists = db.query(Vendor).filter(Vendor.gst_number == payload.gst_number).first() is not None
    pan_exists = db.query(Vendor).filter(Vendor.pan_number == payload.pan_number).first() is not None
    reg_exists = (
        db.query(Vendor)
        .filter(Vendor.company_registration_number == payload.company_registration_number)
        .first()
        is not None
    )

    if not validate_unique_vendor_fields(email_exists, gst_exists, pan_exists, reg_exists):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate email, GST, PAN or registration number",
        )

    vendor_data = payload.model_dump(by_alias=False)
    vendor = Vendor(**vendor_data)

    if hasattr(vendor, "approval_status") and not getattr(vendor, "approval_status", None):
        vendor.approval_status = "Pending"

    if hasattr(vendor, "vendor_status") and not getattr(vendor, "vendor_status", None):
        vendor.vendor_status = "Pending"

    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.get("/", response_model=list[VendorOut])
def list_vendors(
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    approval_status: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Vendor)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Vendor.company_name.ilike(search_term))
            | (Vendor.contact_person_name.ilike(search_term))
            | (Vendor.email.ilike(search_term))
        )

    if category and hasattr(Vendor, "vendor_category"):
        query = query.filter(Vendor.vendor_category == category)

    if status_filter and hasattr(Vendor, "vendor_status"):
        query = query.filter(Vendor.vendor_status == status_filter)

    if approval_status and hasattr(Vendor, "approval_status"):
        query = query.filter(Vendor.approval_status == approval_status)

    return query.all()


@router.get("/{vendor_id}", response_model=VendorOut)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor


@router.patch("/{vendor_id}", response_model=VendorOut)
def update_vendor(vendor_id: int, payload: VendorUpdate, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    update_data = payload.model_dump(exclude_unset=True, by_alias=False)

    if "email" in update_data and update_data["email"] != vendor.email:
        existing = db.query(Vendor).filter(Vendor.email == update_data["email"], Vendor.id != vendor_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    if "gst_number" in update_data and getattr(vendor, "gst_number", None) != update_data["gst_number"]:
        existing = db.query(Vendor).filter(Vendor.gst_number == update_data["gst_number"], Vendor.id != vendor_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GST number already exists")

    if "pan_number" in update_data and getattr(vendor, "pan_number", None) != update_data["pan_number"]:
        existing = db.query(Vendor).filter(Vendor.pan_number == update_data["pan_number"], Vendor.id != vendor_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PAN number already exists")

    if (
        "company_registration_number" in update_data
        and getattr(vendor, "company_registration_number", None) != update_data["company_registration_number"]
    ):
        existing = (
            db.query(Vendor)
            .filter(
                Vendor.company_registration_number == update_data["company_registration_number"],
                Vendor.id != vendor_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company registration number already exists",
            )

    for field, value in update_data.items():
        setattr(vendor, field, value)

    db.commit()
    db.refresh(vendor)
    return vendor


@router.delete("/{vendor_id}", status_code=status.HTTP_200_OK)
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    approval_status = getattr(vendor, "approval_status", None)
    if approval_status == "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approved vendor cannot be deleted",
        )

    db.delete(vendor)
    db.commit()
    return {"message": "Vendor deleted successfully"}


@router.patch("/{vendor_id}/approve", response_model=VendorOut)
def approve_vendor_route(
    vendor_id: int,
    payload: VendorApprovalAction | None = None,
    db: Session = Depends(get_db),
):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    try:
        vendor.approval_status = approve_vendor(getattr(vendor, "approval_status", "Pending"))
        if hasattr(vendor, "vendor_status"):
            vendor.vendor_status = "Active"
        if payload and hasattr(vendor, "approval_remarks"):
            vendor.approval_remarks = payload.remarks
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    db.commit()
    db.refresh(vendor)
    return vendor


@router.patch("/{vendor_id}/reject", response_model=VendorOut)
def reject_vendor_route(
    vendor_id: int,
    payload: VendorApprovalAction | None = None,
    db: Session = Depends(get_db),
):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    try:
        vendor.approval_status = reject_vendor(getattr(vendor, "approval_status", "Pending"))
        if hasattr(vendor, "vendor_status"):
            vendor.vendor_status = "Rejected"
        if payload and hasattr(vendor, "approval_remarks"):
            vendor.approval_remarks = payload.remarks
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    db.commit()
    db.refresh(vendor)
    return vendor


@router.post("/{vendor_id}/documents", response_model=VendorDocumentOut)
async def upload_vendor_document(
    vendor_id: int,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    allowed_types = {
        "GST Certificate",
        "PAN Card",
        "Company Registration Certificate",
        "ISO Certificate",
        "Other Supporting Document",
    }

    if document_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document type",
        )

    return {
        "vendor_id": vendor_id,
        "document_type": document_type,
        "file_name": file.filename,
        "message": "Document metadata accepted. Persist document table/storage after DB coordination.",
    }