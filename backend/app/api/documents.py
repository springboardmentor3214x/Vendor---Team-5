import os
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.vendor_document import VendorDocument
from app.api.auth import get_current_user, normalize_user_role
from app.schemas.document import VendorDocumentOut, VendorDocumentUpdate
from app.services import document_service
from app.api.file_storage import store_document_upload
from app.api.reliability_refresh import refresh_after_compliance_update

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=VendorDocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    vendor_id: int = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Role check: Admins, Managers, or the Vendor themselves
    if normalize_user_role(current_user) == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif normalize_user_role(current_user) not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Save file physically
    file_path = os.path.join(UPLOAD_DIR, f"{vendor_id}_{document_type.replace(' ', '_')}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    doc = VendorDocument(
        vendor_id=vendor_id,
        document_type=document_type,
        file_name=file.filename,
        file_path=file_path,
        content_type=file.content_type,
        uploaded_by=current_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    refresh_after_compliance_update(doc.vendor_id, db)
    return doc


@router.get("/vendor/{vendor_id}", response_model=List[VendorDocumentOut])
def get_vendor_documents(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if normalize_user_role(current_user) == "Vendor":
        from app.models.vendor import Vendor

        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return document_service.get_vendor_documents(db, vendor_id)


@router.post("/{document_id}/replace", response_model=VendorDocumentOut)
async def replace_vendor_document(
    document_id: int,
    document_type: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new current vendor-document version without deleting the prior one."""
    previous = document_service.get_document_by_id(db, document_id)
    if not previous:
        raise HTTPException(status_code=404, detail="Document not found")

    role = normalize_user_role(current_user)
    if role == "Vendor":
        from app.models.vendor import Vendor

        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or vendor.id != previous.vendor_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif role not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    upload = await store_document_upload(file, area="vendor_documents")
    try:
        replacement = document_service.replace_vendor_document(
            db,
            document_id,
            file_name=upload.file_name,
            file_path=upload.file_path,
            file_size=upload.file_size,
            content_type=upload.content_type,
            document_type=document_type.strip() or None,
            uploaded_by=current_user.id,
        )
    except ValueError as error:
        Path(upload.file_path).unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(error)) from error
    if not replacement:
        Path(upload.file_path).unlink(missing_ok=True)
        raise HTTPException(status_code=404, detail="Document not found")
    refresh_after_compliance_update(replacement.vendor_id, db)
    return replacement


@router.get("/{document_id}", response_model=VendorDocumentOut)
def get_document_details(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = document_service.get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if normalize_user_role(current_user) == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or doc.vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return doc


@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = document_service.get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if normalize_user_role(current_user) == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or doc.vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Physical file not found on disk")

    return FileResponse(doc.file_path, filename=doc.file_name, media_type=doc.content_type)


@router.patch("/{document_id}", response_model=VendorDocumentOut)
def update_document_metadata(
    document_id: int,
    payload: VendorDocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update document metadata without replacing the physical uploaded file."""
    doc = document_service.get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if normalize_user_role(current_user) == "Vendor":
        from app.models.vendor import Vendor

        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or doc.vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif normalize_user_role(current_user) not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    changes = payload.model_dump(exclude_unset=True)
    if "document_type" not in changes:
        return doc

    updated_document = document_service.update_document_metadata(
        db,
        document_id,
        changes["document_type"],
    )
    if not updated_document:
        raise HTTPException(status_code=404, detail="Document not found")
    refresh_after_compliance_update(updated_document.vendor_id, db)
    return updated_document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = document_service.get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if normalize_user_role(current_user) == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or doc.vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif normalize_user_role(current_user) not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    vendor_id = doc.vendor_id
    # Delete physical file
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    refresh_after_compliance_update(vendor_id, db)
    return None
