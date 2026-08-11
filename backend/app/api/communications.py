import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, normalize_user_role
from app.core.database import get_db
from app.models.communication import Communication
from app.models.communication_file import CommunicationFile
from app.models.user import User
from app.schemas.communication import CommunicationCreate, CommunicationFileOut, CommunicationResponse
from app.services import communication_service
from app.services.activity_log_service import record_activity_log

router = APIRouter(prefix="/communications", tags=["Communications"])

_MANAGEMENT_ROLES = {"Administrator", "Procurement Manager", "Supply Chain Manager", "Auditor"}
_WRITE_ROLES = {"Administrator", "Procurement Manager", "Supply Chain Manager", "Vendor", "Finance Officer"}
_UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads" / "communications"

# Module 7 communication upload policy. Adjust here if project policy changes.
COMMUNICATION_ALLOWED_EXTENSIONS = {"pdf", "xlsx", "xls", "docx", "doc", "png", "jpg", "jpeg", "zip"}
COMMUNICATION_MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def _visible_query(db: Session, current_user: User):
    query = db.query(Communication)
    role = normalize_user_role(current_user)
    if role in _MANAGEMENT_ROLES:
        return query
    if role == "Vendor":
        from app.models.vendor import Vendor
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if vendor:
            return query.filter(or_(Communication.sender_id == current_user.id, Communication.receiver_id == current_user.id, Communication.vendor_id == vendor.id))
    return query.filter(or_(Communication.sender_id == current_user.id, Communication.receiver_id == current_user.id))


def _require_write_access(current_user: User) -> None:
    if normalize_user_role(current_user) not in _WRITE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to send communications")


@router.post("/", response_model=CommunicationResponse, status_code=status.HTTP_201_CREATED)
def create_communication(payload: CommunicationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _require_write_access(current_user)
    try:
        communication = communication_service.send_message(
            db, sender_id=current_user.id, receiver_id=payload.receiver_id, message=payload.message,
            subject=payload.subject, vendor_id=payload.vendor_id,
            procurement_request_id=payload.procurement_request_id, purchase_order_id=payload.purchase_order_id,
            contract_id=payload.contract_id, invoice_id=payload.invoice_id, discussion_id=payload.discussion_id,
            message_type=payload.message_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    if isinstance(communication, dict):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=communication.get("message", "Communication is unavailable"))
    record_activity_log(db, current_user.id, "MESSAGE_SENT", "Communication", "Communication", communication.id)
    return communication


@router.get("/", response_model=list[CommunicationResponse])
def list_communications(
    sender_id: int | None = Query(default=None), receiver_id: int | None = Query(default=None), vendor_id: int | None = Query(default=None),
    procurement_request_id: int | None = Query(default=None), purchase_order_id: int | None = Query(default=None),
    contract_id: int | None = Query(default=None), invoice_id: int | None = Query(default=None), discussion_id: int | None = Query(default=None),
    message_type: str | None = Query(default=None), is_read: bool | None = Query(default=None),
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    query = _visible_query(db, current_user)
    filters = {"sender_id": sender_id, "receiver_id": receiver_id, "vendor_id": vendor_id,
               "procurement_request_id": procurement_request_id, "purchase_order_id": purchase_order_id,
               "contract_id": contract_id, "invoice_id": invoice_id, "discussion_id": discussion_id,
               "message_type": message_type, "is_read": is_read}
    for field, value in filters.items():
        if value is not None:
            query = query.filter(getattr(Communication, field) == value)
    return query.order_by(Communication.created_at.desc()).all()


@router.post("/files", response_model=CommunicationFileOut, status_code=status.HTTP_201_CREATED)
def upload_communication_file(
    request: Request, file: UploadFile = File(...), message_id: int | None = Form(default=None), discussion_id: int | None = Form(default=None),
    vendor_id: int | None = Form(default=None), procurement_request_id: int | None = Form(default=None),
    purchase_order_id: int | None = Form(default=None), contract_id: int | None = Form(default=None),
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    _require_write_access(current_user)
    if not message_id and not discussion_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="message_id or discussion_id is required")
    if message_id and not _visible_query(db, current_user).filter(Communication.id == message_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Communication not found")
    try:
        filename = communication_service.validate_safe_file_name(file.filename or "")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in COMMUNICATION_ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported communication file type")
    content = file.file.read()
    if len(content) > COMMUNICATION_MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Communication file exceeds the 10 MB limit")
    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination = _UPLOAD_DIR / f"{current_user.id}_{filename}"
    destination.write_bytes(content)
    try:
        stored = communication_service.save_communication_file(
            db, filename, file_path=str(destination), file_type=file.content_type, file_size=len(content),
            uploaded_by_id=current_user.id, message_id=message_id, discussion_id=discussion_id, vendor_id=vendor_id,
            procurement_request_id=procurement_request_id, purchase_order_id=purchase_order_id, contract_id=contract_id,
        )
    except ValueError as exc:
        if destination.exists():
            destination.unlink()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    if isinstance(stored, dict):
        if destination.exists():
            destination.unlink()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=stored.get("message", "File upload is unavailable"))
    record_activity_log(db, current_user.id, "FILE_UPLOADED", "Communication", "CommunicationFile", stored.id, request.client.host if request.client else None)
    return stored


@router.get("/files/list", response_model=list[CommunicationFileOut])
def list_communication_files(message_id: int | None = None, discussion_id: int | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    files = communication_service.list_communication_files(db, message_id=message_id, discussion_id=discussion_id)
    if normalize_user_role(current_user) in _MANAGEMENT_ROLES:
        return files
    return [item for item in files if item.uploaded_by_id == current_user.id or (item.message_id and _visible_query(db, current_user).filter(Communication.id == item.message_id).first())]


@router.get("/files/{file_id}/download")
def download_communication_file(file_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = communication_service.get_communication_file(db, file_id, current_user)
    if not item or isinstance(item, dict):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Communication file not found")
    allowed = normalize_user_role(current_user) in _MANAGEMENT_ROLES or item.uploaded_by_id == current_user.id
    if item.message_id:
        allowed = allowed or bool(_visible_query(db, current_user).filter(Communication.id == item.message_id).first())
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    if not os.path.isfile(item.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File is not available on disk")
    record_activity_log(db, current_user.id, "FILE_DOWNLOADED", "Communication", "CommunicationFile", item.id, request.client.host if request.client else None)
    return FileResponse(item.file_path, filename=item.filename, media_type=item.file_type or "application/octet-stream")


# Keep variable-path routes last: FastAPI evaluates route declarations in order.
@router.get("/{communication_id}", response_model=CommunicationResponse)
def get_communication(communication_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    communication = _visible_query(db, current_user).filter(Communication.id == communication_id).first()
    if not communication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Communication not found")
    record_activity_log(db, current_user.id, "COMMUNICATION_VIEWED", "Communication", "Communication", communication.id, request.client.host if request.client else None)
    return communication


@router.patch("/{communication_id}/read", response_model=CommunicationResponse)
def mark_communication_read(communication_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    communication = communication_service.mark_message_read(db, communication_id, current_user.id)
    if not communication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unread communication for the current user was not found")
    record_activity_log(db, current_user.id, "MESSAGE_READ", "Communication", "Communication", communication.id, request.client.host if request.client else None)
    return communication
