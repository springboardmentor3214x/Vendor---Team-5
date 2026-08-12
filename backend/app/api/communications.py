import os
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, Request
from sqlalchemy import or_
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, normalize_user_role
from app.core.database import get_db
from app.models.user import User
from app.models.communication import Communication
from app.models.communication_file import CommunicationFile
from app.models.contract import Contract
from app.models.discussion import Discussion
from app.models.discussion_participant import DiscussionParticipant
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.vendor import Vendor
from app.schemas.communication import (
    CommunicationCreate,
    CommunicationResponse,
    DiscussionCreate,
    DiscussionResponse,
    CommunicationFileResponse,
    ActivityLogResponse,
)
from app.services.communication_service import (
    send_message,
    fetch_messages,
    mark_message_as_read,
    upload_communication_file,
    list_communication_files,
)
from app.services.discussion_service import (
    create_discussion_thread,
    get_discussion_details,
    list_discussions,
    update_discussion_status,
)
from app.services.activity_log_service import query_activity_logs, log_activity

router = APIRouter(prefix="/communications", tags=["Communications"])

_COMMUNICATION_MANAGEMENT_ROLES = {
    "Administrator",
    "Procurement Manager",
    "Supply Chain Manager",
    "Auditor",
}

# Keep attachment validation at the API boundary.  The service receives only
# already-approved uploads and therefore cannot accidentally persist an unsafe
# file type or an unbounded request body.
ALLOWED_COMMUNICATION_FILE_EXTENSIONS = frozenset({"pdf", "xlsx", "xls", "docx", "doc", "png", "jpg", "jpeg", "zip"})
MAX_COMMUNICATION_FILE_BYTES = int(os.getenv("COMMUNICATION_FILE_MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))


def _validate_communication_file_upload(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file attachment is required")
    extension = Path(file.filename).suffix.lower().lstrip(".")
    if extension not in ALLOWED_COMMUNICATION_FILE_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Unsupported communication file type")

    try:
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
    except (AttributeError, OSError):
        # UploadFile normally exposes a seekable SpooledTemporaryFile.  If a
        # custom stream is not seekable, fail closed instead of bypassing size
        # enforcement.
        raise HTTPException(status_code=413, detail="Unable to validate communication file size")
    if size > MAX_COMMUNICATION_FILE_BYTES:
        raise HTTPException(status_code=413, detail="Communication file exceeds the 10 MB upload limit")


def _communications_query_for_user(db: Session, current_user: User):
    """Return only communication rows visible to the authenticated user."""
    query = db.query(Communication)
    role = normalize_user_role(current_user)
    if role in _COMMUNICATION_MANAGEMENT_ROLES:
        return query

    if role == "Vendor":
        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if vendor:
            return query.filter(
                or_(
                    Communication.sender_id == current_user.id,
                    Communication.receiver_id == current_user.id,
                    Communication.vendor_id == vendor.id,
                )
            )

    return query.filter(or_(Communication.sender_id == current_user.id, Communication.receiver_id == current_user.id))


def _vendor_id_for_user(db: Session, current_user: User) -> int | None:
    vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
    return vendor.id if vendor else None


def _is_discussion_participant(db: Session, discussion_id: int, user_id: int) -> bool:
    return bool(
        db.query(DiscussionParticipant)
        .filter(
            DiscussionParticipant.discussion_id == discussion_id,
            DiscussionParticipant.user_id == user_id,
        )
        .first()
    )


def _can_access_discussion(db: Session, discussion: Discussion, current_user: User) -> bool:
    """Check persisted discussion participation or an explicit linked-record role."""
    role = normalize_user_role(current_user)
    if role == "Administrator" or _is_discussion_participant(db, discussion.id, current_user.id):
        return True

    if role == "Procurement Manager":
        if discussion.purchase_order_id:
            po = db.query(PurchaseOrder).filter(PurchaseOrder.id == discussion.purchase_order_id).first()
            return bool(po and po.assigned_procurement_manager_id == current_user.id)
        if discussion.contract_id:
            contract = db.query(Contract).filter(Contract.id == discussion.contract_id).first()
            return bool(contract and contract.responsible_manager_id == current_user.id)
        if discussion.procurement_request_id:
            procurement_request = (
                db.query(ProcurementRequest)
                .filter(ProcurementRequest.id == discussion.procurement_request_id)
                .first()
            )
            return bool(procurement_request and procurement_request.approved_by == current_user.id)

    if role == "Vendor" and discussion.vendor_id:
        return discussion.vendor_id == _vendor_id_for_user(db, current_user)

    return False


def _require_discussion_access(db: Session, discussion: Discussion, current_user: User) -> None:
    if not _can_access_discussion(db, discussion, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this discussion")


def _can_access_communication_file(db: Session, comm_file: CommunicationFile, current_user: User) -> bool:
    """Scope attachments to their uploader, discussion, or linked business record."""
    role = normalize_user_role(current_user)
    if role == "Administrator" or comm_file.uploaded_by_id == current_user.id:
        return True

    if comm_file.discussion_id:
        discussion = db.query(Discussion).filter(Discussion.id == comm_file.discussion_id).first()
        return bool(discussion and _can_access_discussion(db, discussion, current_user))

    if role == "Vendor":
        own_vendor_id = _vendor_id_for_user(db, current_user)
        if own_vendor_id is None:
            return False
        if comm_file.vendor_id == own_vendor_id:
            return True
        if comm_file.purchase_order_id:
            po = db.query(PurchaseOrder).filter(PurchaseOrder.id == comm_file.purchase_order_id).first()
            return bool(po and po.vendor_id == own_vendor_id)
        if comm_file.contract_id:
            contract = db.query(Contract).filter(Contract.id == comm_file.contract_id).first()
            return bool(contract and contract.vendor_id == own_vendor_id)

    if role == "Procurement Manager" and comm_file.purchase_order_id:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == comm_file.purchase_order_id).first()
        return bool(po and po.assigned_procurement_manager_id == current_user.id)

    return False


# --- Vendor Messaging System ---

@router.post("/", response_model=CommunicationResponse)
def create_message_endpoint(
    payload: CommunicationCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send vendor message or reply attached to procurement record."""
    client_ip = request.client.host if request.client else None
    # Sender identity is derived from the authenticated user, never from payload.
    return send_message(db=db, payload=payload, sender_user_id=current_user.id, ip_address=client_ip)


@router.get("/", response_model=List[CommunicationResponse])
def list_messages_endpoint(
    vendor_id: Optional[int] = Query(None, alias="vendorId"),
    purchase_order_id: Optional[int] = Query(None, alias="purchaseOrderId"),
    contract_id: Optional[int] = Query(None, alias="contractId"),
    procurement_request_id: Optional[int] = Query(None, alias="procurementRequestId"),
    discussion_id: Optional[int] = Query(None, alias="discussionId"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch communication messages filtered by procurement entities."""
    # Keep API-layer role visibility restrictions in addition to entity filters.
    messages = fetch_messages(
        db=db,
        vendor_id=vendor_id,
        purchase_order_id=purchase_order_id,
        contract_id=contract_id,
        procurement_request_id=procurement_request_id,
        discussion_id=discussion_id,
        user_id=current_user.id,
    )
    visible_ids = {row.id for row in _communications_query_for_user(db, current_user).all()}
    return [row for row in messages if row.id in visible_ids]


@router.get("/{communication_id:int}", response_model=CommunicationResponse)
def get_communication(
    communication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    communication = _communications_query_for_user(db, current_user).filter(Communication.id == communication_id).first()
    if not communication:
        raise HTTPException(status_code=404, detail="Communication not found")
    return communication


@router.post("/{message_id}/read", response_model=CommunicationResponse)
def mark_read_endpoint(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a communication message as read."""
    message = _communications_query_for_user(db, current_user).filter(Communication.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return mark_message_as_read(db=db, message_id=message_id, user_id=current_user.id)


# --- Procurement Discussions ---

@router.post("/discussions", response_model=DiscussionResponse)
def create_discussion_endpoint(
    payload: DiscussionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a multi-stakeholder procurement discussion thread."""
    client_ip = request.client.host if request.client else None
    return create_discussion_thread(db=db, payload=payload, creator_user_id=current_user.id, ip_address=client_ip)


@router.get("/discussions", response_model=List[DiscussionResponse])
def list_discussions_endpoint(
    vendor_id: Optional[int] = Query(None, alias="vendorId"),
    purchase_order_id: Optional[int] = Query(None, alias="purchaseOrderId"),
    contract_id: Optional[int] = Query(None, alias="contractId"),
    procurement_request_id: Optional[int] = Query(None, alias="procurementRequestId"),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List procurement discussions with optional filters."""
    discussions = list_discussions(
        db=db,
        vendor_id=vendor_id,
        purchase_order_id=purchase_order_id,
        contract_id=contract_id,
        procurement_request_id=procurement_request_id,
        status=status,
    )
    return [discussion for discussion in discussions if _can_access_discussion(db, discussion, current_user)]


@router.get("/discussions/{discussion_id}", response_model=DiscussionResponse)
def get_discussion_endpoint(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get discussion details and threaded messages."""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion thread not found")
    _require_discussion_access(db, discussion, current_user)
    return get_discussion_details(db=db, discussion_id=discussion_id)


@router.patch("/discussions/{discussion_id}/status", response_model=DiscussionResponse)
def update_discussion_status_endpoint(
    discussion_id: int,
    status: str = Query(..., description="OPEN, RESOLVED, or CLOSED"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update discussion status (OPEN, RESOLVED, CLOSED)."""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion thread not found")
    _require_discussion_access(db, discussion, current_user)
    return update_discussion_status(db=db, discussion_id=discussion_id, status=status, user_id=current_user.id)


# --- File Sharing ---

@router.post("/files/upload", response_model=CommunicationFileResponse)
def upload_file_endpoint(
    request: Request,
    file: UploadFile = File(...),
    vendor_id: Optional[int] = Form(None, alias="vendorId"),
    purchase_order_id: Optional[int] = Form(None, alias="purchaseOrderId"),
    contract_id: Optional[int] = Form(None, alias="contractId"),
    discussion_id: Optional[int] = Form(None, alias="discussionId"),
    message_id: Optional[int] = Form(None, alias="messageId"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload document attachment linked to vendor, PO, contract, or discussion."""
    client_ip = request.client.host if request.client else None
    _validate_communication_file_upload(file)
    if discussion_id:
        discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
        if not discussion:
            raise HTTPException(status_code=404, detail="Discussion thread not found")
        _require_discussion_access(db, discussion, current_user)
    elif normalize_user_role(current_user) == "Vendor":
        own_vendor_id = _vendor_id_for_user(db, current_user)
        if vendor_id is not None and vendor_id != own_vendor_id:
            raise HTTPException(status_code=403, detail="You can only attach files to your own vendor record")
        if purchase_order_id:
            po = db.query(PurchaseOrder).filter(PurchaseOrder.id == purchase_order_id).first()
            if not po or po.vendor_id != own_vendor_id:
                raise HTTPException(status_code=403, detail="You can only attach files to your own purchase order")
        if contract_id:
            contract = db.query(Contract).filter(Contract.id == contract_id).first()
            if not contract or contract.vendor_id != own_vendor_id:
                raise HTTPException(status_code=403, detail="You can only attach files to your own contract")
    return upload_communication_file(
        db=db,
        file=file,
        uploaded_by_id=current_user.id,
        vendor_id=vendor_id,
        purchase_order_id=purchase_order_id,
        contract_id=contract_id,
        discussion_id=discussion_id,
        message_id=message_id,
        ip_address=client_ip,
    )


@router.get("/files", response_model=List[CommunicationFileResponse])
def list_files_endpoint(
    vendor_id: Optional[int] = Query(None, alias="vendorId"),
    purchase_order_id: Optional[int] = Query(None, alias="purchaseOrderId"),
    contract_id: Optional[int] = Query(None, alias="contractId"),
    discussion_id: Optional[int] = Query(None, alias="discussionId"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List shared communication files."""
    files = list_communication_files(
        db=db,
        vendor_id=vendor_id,
        purchase_order_id=purchase_order_id,
        contract_id=contract_id,
        discussion_id=discussion_id,
    )
    return [comm_file for comm_file in files if _can_access_communication_file(db, comm_file, current_user)]


@router.get("/files/{file_id}/download")
def download_file_endpoint(
    file_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download communication file attachment."""
    comm_file = db.query(CommunicationFile).filter(CommunicationFile.id == file_id).first()
    if not comm_file:
        raise HTTPException(status_code=404, detail="File attachment not found")
    if not _can_access_communication_file(db, comm_file, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this file attachment")
    if not os.path.exists(comm_file.file_path):
        raise HTTPException(status_code=404, detail="File attachment not found")

    client_ip = request.client.host if request.client else None
    log_activity(
        db=db,
        user_id=current_user.id,
        module="Communication",
        action="FILE_DOWNLOADED",
        description=f"Downloaded file '{comm_file.filename}'",
        related_entity_type="CommunicationFile",
        related_entity_id=comm_file.id,
        ip_address=client_ip,
    )

    return FileResponse(
        path=comm_file.file_path,
        filename=comm_file.filename,
        media_type=comm_file.file_type or "application/octet-stream",
    )


# --- Activity Logs ---

@router.get("/activity-logs", response_model=List[ActivityLogResponse])
def get_activity_logs_endpoint(
    module: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None, alias="userId"),
    action: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Query and filter system activity logs for audit trail."""
    role = normalize_user_role(current_user)
    if role not in {"Administrator", "Auditor"}:
        if user_id is not None and user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only view your own activity logs")
        user_id = current_user.id
    return query_activity_logs(
        db=db,
        module=module,
        user_id=user_id,
        action=action,
        limit=limit,
        offset=offset,
    )
