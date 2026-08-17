import os
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile

from app.models.communication import Communication
from app.models.communication_file import CommunicationFile
from app.models.user import User
from app.schemas.communication import CommunicationCreate
from app.services.activity_log_service import log_activity
from app.services.notification_service import create_notification

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "communication_files")


def send_message(
    db: Session,
    payload: CommunicationCreate,
    sender_user_id: int,
    ip_address: Optional[str] = None
) -> Communication:
    """Send vendor message or discussion reply attached to procurement record."""
    message = Communication(
        sender_id=sender_user_id,
        receiver_id=payload.receiver_id,
        vendor_id=payload.vendor_id,
        procurement_request_id=payload.procurement_request_id,
        purchase_order_id=payload.purchase_order_id,
        contract_id=payload.contract_id,
        invoice_id=payload.invoice_id,
        discussion_id=payload.discussion_id,
        subject=payload.subject,
        message=payload.message,
        message_type=payload.message_type or "DIRECT",
        is_read=False
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    # Trigger notification to receiver if receiver_id is specified
    if payload.receiver_id and payload.receiver_id != sender_user_id:
        create_notification(
            db=db,
            user_id=payload.receiver_id,
            title="New Communication Message",
            message=f"You received a message: '{payload.subject or payload.message[:50]}...'",
            notification_type="INFO",
            related_entity_id=message.id
        )

    # Activity Log
    entity_type = "PurchaseOrder" if payload.purchase_order_id else (
        "Contract" if payload.contract_id else (
            "Vendor" if payload.vendor_id else (
                "Discussion" if payload.discussion_id else "Communication"
            )
        )
    )
    entity_id = payload.purchase_order_id or payload.contract_id or payload.vendor_id or payload.discussion_id or message.id

    log_activity(
        db=db,
        user_id=sender_user_id,
        module="Communication",
        action="MESSAGE_SENT",
        description=f"Sent {message.message_type} message (ID: {message.id})",
        related_entity_type=entity_type,
        related_entity_id=entity_id,
        ip_address=ip_address
    )

    return message


def mark_message_as_read(db: Session, message_id: int, user_id: int) -> Communication:
    """Mark message read status and timestamp."""
    message = db.query(Communication).filter(Communication.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.receiver_id != user_id:
        raise HTTPException(status_code=403, detail="Only the message receiver can mark it as read")

    message.is_read = True
    message.read_at = datetime.utcnow()
    db.commit()
    db.refresh(message)

    log_activity(
        db=db,
        user_id=user_id,
        module="Communication",
        action="MESSAGE_READ",
        description=f"Marked message {message_id} as read",
        related_entity_type="Communication",
        related_entity_id=message_id
    )

    return message


def fetch_messages(
    db: Session,
    vendor_id: Optional[int] = None,
    purchase_order_id: Optional[int] = None,
    contract_id: Optional[int] = None,
    procurement_request_id: Optional[int] = None,
    discussion_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> List[Communication]:
    """Fetch communication messages filtered by business entity or discussion."""
    query = db.query(Communication)
    if discussion_id:
        query = query.filter(Communication.discussion_id == discussion_id)
    if vendor_id:
        query = query.filter(Communication.vendor_id == vendor_id)
    if purchase_order_id:
        query = query.filter(Communication.purchase_order_id == purchase_order_id)
    if contract_id:
        query = query.filter(Communication.contract_id == contract_id)
    if procurement_request_id:
        query = query.filter(Communication.procurement_request_id == procurement_request_id)
    if user_id:
        query = query.filter(
            (Communication.sender_id == user_id) | (Communication.receiver_id == user_id)
        )

    return query.order_by(Communication.created_at.asc()).all()


def upload_communication_file(
    db: Session,
    file: UploadFile,
    uploaded_by_id: int,
    vendor_id: Optional[int] = None,
    purchase_order_id: Optional[int] = None,
    contract_id: Optional[int] = None,
    discussion_id: Optional[int] = None,
    message_id: Optional[int] = None,
    ip_address: Optional[str] = None
) -> CommunicationFile:
    """Save communication file attachment to local storage and DB."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    file_content = file.file.read()
    with open(file_path, "wb") as f:
        f.write(file_content)

    comm_file = CommunicationFile(
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=len(file_content),
        uploaded_by_id=uploaded_by_id,
        vendor_id=vendor_id,
        purchase_order_id=purchase_order_id,
        contract_id=contract_id,
        discussion_id=discussion_id,
        message_id=message_id
    )
    db.add(comm_file)
    db.commit()
    db.refresh(comm_file)

    log_activity(
        db=db,
        user_id=uploaded_by_id,
        module="Communication",
        action="FILE_UPLOADED",
        description=f"Uploaded file '{file.filename}'",
        related_entity_type="CommunicationFile",
        related_entity_id=comm_file.id,
        ip_address=ip_address
    )

    return comm_file


def list_communication_files(
    db: Session,
    vendor_id: Optional[int] = None,
    purchase_order_id: Optional[int] = None,
    contract_id: Optional[int] = None,
    discussion_id: Optional[int] = None
) -> List[CommunicationFile]:
    """Retrieve shared files linked to vendor or procurement record."""
    query = db.query(CommunicationFile)
    if vendor_id:
        query = query.filter(CommunicationFile.vendor_id == vendor_id)
    if purchase_order_id:
        query = query.filter(CommunicationFile.purchase_order_id == purchase_order_id)
    if contract_id:
        query = query.filter(CommunicationFile.contract_id == contract_id)
    if discussion_id:
        query = query.filter(CommunicationFile.discussion_id == discussion_id)

    return query.order_by(CommunicationFile.created_at.desc()).all()
