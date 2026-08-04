from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.discussion import Discussion
from app.models.discussion_participant import DiscussionParticipant
from app.models.communication import Communication
from app.models.user import User
from app.schemas.communication import DiscussionCreate
from app.services.activity_log_service import log_activity
from app.services.notification_service import create_notification


def create_discussion_thread(
    db: Session,
    payload: DiscussionCreate,
    creator_user_id: int,
    ip_address: Optional[str] = None
) -> Discussion:
    """Create a new procurement discussion thread attached to a business entity."""
    discussion = Discussion(
        title=payload.title,
        created_by_id=creator_user_id,
        vendor_id=payload.vendor_id,
        procurement_request_id=payload.procurement_request_id,
        purchase_order_id=payload.purchase_order_id,
        contract_id=payload.contract_id,
        invoice_id=payload.invoice_id,
        status="OPEN"
    )
    db.add(discussion)
    db.commit()
    db.refresh(discussion)

    # Add creator as participant
    creator_participant = DiscussionParticipant(
        discussion_id=discussion.id,
        user_id=creator_user_id
    )
    db.add(creator_participant)

    # Add other specified participants
    if payload.participant_user_ids:
        for u_id in payload.participant_user_ids:
            if u_id != creator_user_id:
                participant = DiscussionParticipant(
                    discussion_id=discussion.id,
                    user_id=u_id
                )
                db.add(participant)

                # Send in-app notification to participants
                create_notification(
                    db=db,
                    user_id=u_id,
                    title="Added to Discussion",
                    message=f"You have been added to procurement discussion: '{discussion.title}'",
                    notification_type="INFO",
                    related_entity_id=discussion.id
                )

    # Add initial message if provided
    if payload.initial_message:
        init_msg = Communication(
            sender_id=creator_user_id,
            vendor_id=payload.vendor_id,
            procurement_request_id=payload.procurement_request_id,
            purchase_order_id=payload.purchase_order_id,
            contract_id=payload.contract_id,
            invoice_id=payload.invoice_id,
            discussion_id=discussion.id,
            subject=payload.title,
            message=payload.initial_message,
            message_type="DISCUSSION"
        )
        db.add(init_msg)

    db.commit()
    db.refresh(discussion)

    # Audit Log
    entity_type = "PurchaseOrder" if payload.purchase_order_id else (
        "Contract" if payload.contract_id else (
            "ProcurementRequest" if payload.procurement_request_id else (
                "Vendor" if payload.vendor_id else "Discussion"
            )
        )
    )
    entity_id = payload.purchase_order_id or payload.contract_id or payload.procurement_request_id or payload.vendor_id or discussion.id

    log_activity(
        db=db,
        user_id=creator_user_id,
        module="Communication",
        action="DISCUSSION_CREATED",
        description=f"Created discussion thread '{discussion.title}'",
        related_entity_type=entity_type,
        related_entity_id=entity_id,
        ip_address=ip_address
    )

    return discussion


def get_discussion_details(db: Session, discussion_id: int) -> Discussion:
    """Fetch discussion details along with threaded messages."""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion thread not found")
    return discussion


def list_discussions(
    db: Session,
    vendor_id: Optional[int] = None,
    purchase_order_id: Optional[int] = None,
    contract_id: Optional[int] = None,
    procurement_request_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[Discussion]:
    """Query discussions filtered by procurement records."""
    query = db.query(Discussion)
    if vendor_id:
        query = query.filter(Discussion.vendor_id == vendor_id)
    if purchase_order_id:
        query = query.filter(Discussion.purchase_order_id == purchase_order_id)
    if contract_id:
        query = query.filter(Discussion.contract_id == contract_id)
    if procurement_request_id:
        query = query.filter(Discussion.procurement_request_id == procurement_request_id)
    if status:
        query = query.filter(Discussion.status == status)

    return query.order_by(Discussion.updated_at.desc()).all()


def update_discussion_status(db: Session, discussion_id: int, status: str, user_id: int) -> Discussion:
    """Update discussion status (OPEN, RESOLVED, CLOSED)."""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion thread not found")

    discussion.status = status
    discussion.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(discussion)

    log_activity(
        db=db,
        user_id=user_id,
        module="Communication",
        action="DISCUSSION_STATUS_UPDATED",
        description=f"Discussion '{discussion.title}' status changed to {status}",
        related_entity_type="Discussion",
        related_entity_id=discussion.id
    )

    return discussion
