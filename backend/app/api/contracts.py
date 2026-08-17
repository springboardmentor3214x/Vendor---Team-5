from typing import List
from datetime import datetime, timedelta

import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.vendor import Vendor
from app.api.auth import get_current_user, normalize_user_role
from app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractRenewalCreate,
    ContractRenewalOut
)
from app.schemas.document_lifecycle import LifecycleDocumentOut
from app.services import contract_service
from app.services import contract_document_service
from app.api.file_storage import store_document_upload
from app.api.reliability_refresh import refresh_after_compliance_update

router = APIRouter(prefix="/contracts", tags=["Contracts"])


def _contract_document_response(document) -> dict:
    return {
        "id": document.id,
        "document_type": document.document_type,
        "file_name": document.file_name,
        "file_size": document.file_size,
        "content_type": document.content_type,
        "uploaded_by": document.uploaded_by,
        "uploaded_at": document.uploaded_at,
        "version": document.version or 1,
        "is_current": bool(document.is_current),
        "replaced_document_id": document.replaced_document_id,
        "replaced_at": document.replaced_at,
        "replaced_by": document.replaced_by,
    }


def _require_contract_document_access(db: Session, contract_id: int, current_user: User, *, write: bool):
    contract = contract_service.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    role = normalize_user_role(current_user)
    if role == "Vendor":
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or vendor.id != contract.vendor_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif role not in {"Administrator", "Procurement Manager", "Supply Chain Manager", "Auditor", "Finance Officer"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if write and role not in {"Administrator", "Procurement Manager", "Vendor"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to modify contract documents")
    return contract


@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(payload: ContractCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if normalize_user_role(current_user) not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators or Procurement Managers can create contracts"
        )
    
    contract = contract_service.create_contract(db, payload)
    refresh_after_compliance_update(contract.vendor_id, db)
    return contract


@router.get("/", response_model=List[ContractResponse])
def list_contracts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if normalize_user_role(current_user) == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor:
            return []
        return db.query(contract_service.Contract).filter(contract_service.Contract.vendor_id == vendor.id).order_by(contract_service.Contract.id.desc()).all()
        
    return db.query(contract_service.Contract).order_by(contract_service.Contract.id.desc()).all()


@router.get("/expiring", response_model=List[ContractResponse])
def get_expiring_contracts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if normalize_user_role(current_user) not in ["Administrator", "Procurement Manager", "Supply Chain Manager", "Auditor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return contract_service.get_expiring_contracts(db)


@router.get("/{contract_id}/documents", response_model=List[LifecycleDocumentOut])
def list_contract_documents(
    contract_id: int,
    include_replaced: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_contract_document_access(db, contract_id, current_user, write=False)
    documents = contract_document_service.list_contract_documents(
        db, contract_id, include_replaced=include_replaced
    )
    return [_contract_document_response(document) for document in documents]


@router.post("/{contract_id}/documents", response_model=LifecycleDocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_contract_document(
    contract_id: int,
    document_type: str = Form("Signed Agreement"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_contract_document_access(db, contract_id, current_user, write=True)
    if not document_type.strip():
        raise HTTPException(status_code=400, detail="Document type is required")
    upload = await store_document_upload(file, area="contract_documents")
    document = contract_document_service.create_contract_document(
        db,
        contract_id=contract_id,
        document_type=document_type.strip(),
        file_name=upload.file_name,
        file_path=upload.file_path,
        file_size=upload.file_size,
        content_type=upload.content_type,
        uploaded_by=current_user.id,
    )
    return _contract_document_response(document)


@router.get("/{contract_id}/documents/{document_id}/download")
def download_contract_document(
    contract_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_contract_document_access(db, contract_id, current_user, write=False)
    document = contract_document_service.get_contract_document(db, document_id)
    if not document or document.contract_id != contract_id:
        raise HTTPException(status_code=404, detail="Contract document not found")
    if not document.file_path or not os.path.isfile(document.file_path):
        raise HTTPException(status_code=404, detail="Physical file not found on disk")
    return FileResponse(document.file_path, filename=document.file_name, media_type=document.content_type)


@router.post("/{contract_id}/documents/{document_id}/replace", response_model=LifecycleDocumentOut)
async def replace_contract_document(
    contract_id: int,
    document_id: int,
    document_type: str = Form("Signed Agreement"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_contract_document_access(db, contract_id, current_user, write=True)
    existing = contract_document_service.get_contract_document(db, document_id)
    if not existing or existing.contract_id != contract_id:
        raise HTTPException(status_code=404, detail="Contract document not found")
    upload = await store_document_upload(file, area="contract_documents")
    try:
        replacement = contract_document_service.replace_contract_document(
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
        raise HTTPException(status_code=404, detail="Contract document not found")
    return _contract_document_response(replacement)


@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(contract_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contract = contract_service.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    if normalize_user_role(current_user) == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if not vendor or contract.vendor_id != vendor.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            
    return contract


@router.patch("/{contract_id}", response_model=ContractResponse)
def update_contract(contract_id: int, payload: ContractUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if normalize_user_role(current_user) not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators or Procurement Managers can update contracts"
        )
        
    contract = contract_service.update_contract(db, contract_id, payload)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    refresh_after_compliance_update(contract.vendor_id, db)
        
    return contract


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(contract_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if normalize_user_role(current_user) not in ["Administrator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators can delete contracts"
        )
        
    contract = contract_service.get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    contract_service.delete_contract(db, contract_id)
    refresh_after_compliance_update(contract.vendor_id, db)


@router.post("/{contract_id}/renew", response_model=ContractResponse)
def renew_contract(contract_id: int, payload: ContractRenewalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if normalize_user_role(current_user) not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators or Procurement Managers can renew contracts"
        )
        
    contract = contract_service.renew_contract(db, contract_id, payload)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    refresh_after_compliance_update(contract.vendor_id, db)
        
    return contract


@router.patch("/{contract_id}/status", response_model=ContractResponse)
def update_contract_status(contract_id: int, status_str: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if normalize_user_role(current_user) not in ["Administrator", "Procurement Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
        
    contract = contract_service.update_contract_status(db, contract_id, status_str)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    refresh_after_compliance_update(contract.vendor_id, db)
        
    return contract
