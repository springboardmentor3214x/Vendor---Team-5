"""JWT-scoped API for dedicated one-to-one messages (Module 7)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, normalize_user_role
from app.core.database import get_db
from app.models.contract import Contract
from app.models.message import Message, RelatedEntityType
from app.models.procurement_request import ProcurementRequest
from app.models.purchase_order import PurchaseOrder
from app.models.user import User
from app.models.vendor import Vendor
from app.schemas.messages import ConversationSummary, MessageContact, MessageCreate, MessageOut, UnreadMessageCountOut
from app.services import message_service

router = APIRouter(prefix="/messages", tags=["Messages"])


def _vendor_id_for_user(db: Session, current_user: User) -> Optional[int]:
    vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
    return vendor.id if vendor else None


def _require_related_entity_access(
    db: Session,
    current_user: User,
    entity_type: RelatedEntityType,
    entity_id: Optional[int],
) -> None:
    """Use the same business-record visibility principles as Communications."""
    if entity_type == RelatedEntityType.NONE:
        if entity_id is not None:
            raise HTTPException(status_code=400, detail="relatedEntityId requires a relatedEntityType")
        return
    if entity_id is None:
        raise HTTPException(status_code=400, detail="relatedEntityId is required for a related entity")

    role = normalize_user_role(current_user)
    if role == "Administrator":
        return

    if entity_type == RelatedEntityType.VENDOR:
        vendor = db.query(Vendor).filter(Vendor.id == entity_id).first()
        if not vendor:
            raise HTTPException(status_code=404, detail="Related vendor not found")
        if role == "Vendor" and vendor.id == _vendor_id_for_user(db, current_user):
            return
        if role in {"Procurement Manager", "Supply Chain Manager"}:
            return
        raise HTTPException(status_code=403, detail="You do not have access to this vendor context")

    if entity_type == RelatedEntityType.PURCHASE_ORDER:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == entity_id).first()
        if not po:
            raise HTTPException(status_code=404, detail="Related purchase order not found")
        if role == "Vendor" and po.vendor_id == _vendor_id_for_user(db, current_user):
            return
        if role == "Procurement Manager" and (
            po.assigned_procurement_manager_id == current_user.id or po.created_by == current_user.id
        ):
            return
        if role == "Supply Chain Manager":
            return
        raise HTTPException(status_code=403, detail="You do not have access to this purchase order context")

    if entity_type == RelatedEntityType.PROCUREMENT_REQUEST:
        request = db.query(ProcurementRequest).filter(ProcurementRequest.id == entity_id).first()
        if not request:
            raise HTTPException(status_code=404, detail="Related procurement request not found")
        if role == "Vendor" and request.vendor_id == _vendor_id_for_user(db, current_user):
            return
        if role == "Procurement Manager" and request.approved_by == current_user.id:
            return
        if role == "Department User" and request.created_by == current_user.id:
            return
        if role == "Supply Chain Manager":
            return
        raise HTTPException(status_code=403, detail="You do not have access to this procurement request context")

    if entity_type == RelatedEntityType.CONTRACT:
        contract = db.query(Contract).filter(Contract.id == entity_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Related contract not found")
        if role == "Vendor" and contract.vendor_id == _vendor_id_for_user(db, current_user):
            return
        if role == "Procurement Manager" and contract.responsible_manager_id == current_user.id:
            return
        raise HTTPException(status_code=403, detail="You do not have access to this contract context")


def _message_out(message: Message) -> MessageOut:
    return MessageOut.model_validate(message)


def _message_contact(user: User) -> MessageContact:
    return MessageContact(
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=normalize_user_role(user),
    )


def _user_for_vendor(db: Session, vendor_id: int) -> Optional[User]:
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        return None
    return db.query(User).filter(User.email == vendor.email, User.is_active.is_(True)).first()


def _context_contacts(
    db: Session,
    current_user: User,
    related_entity_type: RelatedEntityType,
    related_entity_id: int,
) -> list[User]:
    """Return real message participants after the caller has passed context access."""
    candidates: list[User] = []

    if related_entity_type == RelatedEntityType.VENDOR:
        user = _user_for_vendor(db, related_entity_id)
        if user:
            candidates.append(user)
    elif related_entity_type == RelatedEntityType.PURCHASE_ORDER:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == related_entity_id).first()
        if po:
            vendor_user = _user_for_vendor(db, po.vendor_id)
            if vendor_user:
                candidates.append(vendor_user)
            for user_id in (po.assigned_procurement_manager_id, po.created_by):
                if user_id:
                    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
                    if user:
                        candidates.append(user)
    elif related_entity_type == RelatedEntityType.PROCUREMENT_REQUEST:
        request = db.query(ProcurementRequest).filter(ProcurementRequest.id == related_entity_id).first()
        if request:
            vendor_user = _user_for_vendor(db, request.vendor_id) if request.vendor_id else None
            if vendor_user:
                candidates.append(vendor_user)
            for user_id in (request.created_by, request.approved_by):
                if user_id:
                    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
                    if user:
                        candidates.append(user)
    elif related_entity_type == RelatedEntityType.CONTRACT:
        contract = db.query(Contract).filter(Contract.id == related_entity_id).first()
        if contract:
            vendor_user = _user_for_vendor(db, contract.vendor_id)
            if vendor_user:
                candidates.append(vendor_user)
            if contract.responsible_manager_id:
                manager = db.query(User).filter(
                    User.id == contract.responsible_manager_id,
                    User.is_active.is_(True),
                ).first()
                if manager:
                    candidates.append(manager)

    return list({user.id: user for user in candidates if user.id != current_user.id}.values())


@router.get("/contacts", response_model=list[MessageContact])
def get_message_contacts(
    related_entity_type: RelatedEntityType = Query(alias="relatedEntityType"),
    related_entity_id: int = Query(alias="relatedEntityId", gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resolve only real recipients participating in an accessible record context."""
    _require_related_entity_access(db, current_user, related_entity_type, related_entity_id)
    return [_message_contact(user) for user in _context_contacts(
        db, current_user, related_entity_type, related_entity_id
    )]


@router.post("", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=MessageOut, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def send_direct_message(
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a direct message; sender identity is always taken from the JWT."""
    receiver = db.query(User).filter(User.id == payload.receiver_id).first()
    if not receiver or not getattr(receiver, "is_active", True):
        raise HTTPException(status_code=404, detail="Message receiver not found")
    if receiver.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot send a direct message to yourself")

    _require_related_entity_access(
        db,
        current_user,
        payload.related_entity_type,
        payload.related_entity_id,
    )
    if payload.related_entity_type != RelatedEntityType.NONE:
        allowed_receivers = {
            user.id for user in _context_contacts(
                db,
                current_user,
                payload.related_entity_type,
                payload.related_entity_id,
            )
        }
        if receiver.id not in allowed_receivers:
            raise HTTPException(
                status_code=403,
                detail="The message receiver is not a participant in the selected record context",
            )
    message = message_service.send_message(
        db,
        sender_id=current_user.id,
        receiver_id=receiver.id,
        content=payload.content,
        related_entity_type=payload.related_entity_type,
        related_entity_id=payload.related_entity_id,
    )

    # `message_service.send_message` persists the receiver-facing in-app
    # notification. Keeping that side effect in one place prevents duplicate
    # alerts for a single direct message.
    return _message_out(message)


@router.get("/conversations", response_model=list[ConversationSummary])
def get_conversations(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return message_service.list_conversations(db, user_id=current_user.id, limit=limit, offset=offset)


@router.get("/conversations/{other_user_id}", response_model=list[MessageOut])
def get_direct_conversation(
    other_user_id: int,
    related_entity_type: Optional[RelatedEntityType] = Query(None, alias="relatedEntityType"),
    related_entity_id: Optional[int] = Query(None, alias="relatedEntityId", gt=0),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.query(User).filter(User.id == other_user_id).first():
        raise HTTPException(status_code=404, detail="Conversation user not found")
    if related_entity_type is not None:
        _require_related_entity_access(db, current_user, related_entity_type, related_entity_id)
    return [
        _message_out(message)
        for message in message_service.get_conversation(
            db,
            user_a_id=current_user.id,
            user_b_id=other_user_id,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            limit=limit,
            offset=offset,
        )
    ]


@router.get("/unread-count", response_model=UnreadMessageCountOut)
def get_unread_message_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {"unread": message_service.get_unread_count(db, user_id=current_user.id)}


@router.patch("/{message_id}/read", response_model=MessageOut)
def mark_direct_message_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the message receiver can mark it as read")
    updated = message_service.mark_as_read(db, message_id=message_id, reader_id=current_user.id)
    if not updated:  # Defensive guard for a concurrent ownership change.
        raise HTTPException(status_code=404, detail="Message not found")
    return _message_out(updated)
