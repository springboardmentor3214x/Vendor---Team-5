from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, normalize_user_role
from app.core.database import get_db
from app.models.communication import Communication
from app.models.discussion import Discussion
from app.models.discussion_participant import DiscussionParticipant
from app.models.user import User
from app.schemas.communication import (
    CommunicationResponse, DiscussionCreate, DiscussionDetailOut, DiscussionOut,
    DiscussionParticipantCreate, DiscussionParticipantOut,
)
from app.services import communication_service
from app.services.activity_log_service import record_activity_log

router = APIRouter(prefix="/discussions", tags=["Discussions"])
_MANAGEMENT_ROLES = {"Administrator", "Procurement Manager", "Supply Chain Manager", "Auditor"}
_WRITE_ROLES = {"Administrator", "Procurement Manager", "Supply Chain Manager", "Vendor", "Finance Officer"}


def _is_participant(db: Session, discussion_id: int, user_id: int) -> bool:
    return db.query(DiscussionParticipant).filter(
        DiscussionParticipant.discussion_id == discussion_id, DiscussionParticipant.user_id == user_id
    ).first() is not None


def _can_access(db: Session, discussion: Discussion, user: User) -> bool:
    return normalize_user_role(user) in _MANAGEMENT_ROLES or discussion.created_by_id == user.id or _is_participant(db, discussion.id, user.id)


def _get_accessible(db: Session, discussion_id: int, user: User) -> Discussion:
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discussion not found")
    if not _can_access(db, discussion, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return discussion


@router.post("/", response_model=DiscussionOut, status_code=status.HTTP_201_CREATED)
def create_discussion(payload: DiscussionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if normalize_user_role(current_user) not in _WRITE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    try:
        discussion = communication_service.create_discussion(
            db, current_user.id, payload.title, payload.participant_ids, vendor_id=payload.vendor_id,
            procurement_request_id=payload.procurement_request_id, purchase_order_id=payload.purchase_order_id,
            contract_id=payload.contract_id, invoice_id=payload.invoice_id, status=payload.status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    if isinstance(discussion, dict):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=discussion.get("message", "Discussion is unavailable"))
    record_activity_log(db, current_user.id, "DISCUSSION_CREATED", "Communication", "Discussion", discussion.id)
    return discussion


@router.get("/", response_model=list[DiscussionOut])
def list_discussions(
    vendor_id: int | None = Query(default=None), procurement_request_id: int | None = Query(default=None),
    purchase_order_id: int | None = Query(default=None), contract_id: int | None = Query(default=None),
    invoice_id: int | None = Query(default=None), status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    filters = {"vendor_id": vendor_id, "procurement_request_id": procurement_request_id, "purchase_order_id": purchase_order_id,
               "contract_id": contract_id, "invoice_id": invoice_id, "status": status_filter}
    rows = communication_service.list_discussions(db, {key: value for key, value in filters.items() if value is not None})
    return rows if normalize_user_role(current_user) in _MANAGEMENT_ROLES else [row for row in rows if _can_access(db, row, current_user)]


@router.get("/{discussion_id}", response_model=DiscussionDetailOut)
def get_discussion(discussion_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    discussion = _get_accessible(db, discussion_id, current_user)
    participants = db.query(DiscussionParticipant).filter(DiscussionParticipant.discussion_id == discussion_id).all()
    messages = db.query(Communication).filter(Communication.discussion_id == discussion_id).order_by(Communication.created_at.asc()).all()
    return DiscussionDetailOut(
        **DiscussionOut.model_validate(discussion).model_dump(),
        participants=[DiscussionParticipantOut.model_validate(item) for item in participants],
        messages=[CommunicationResponse.model_validate(item) for item in messages],
    )


@router.post("/{discussion_id}/participants", response_model=DiscussionParticipantOut, status_code=status.HTTP_201_CREATED)
def add_discussion_participant(discussion_id: int, payload: DiscussionParticipantCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    discussion = _get_accessible(db, discussion_id, current_user)
    if normalize_user_role(current_user) not in _MANAGEMENT_ROLES and discussion.created_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the discussion creator or a manager can add participants")
    existing = db.query(DiscussionParticipant).filter(DiscussionParticipant.discussion_id == discussion_id, DiscussionParticipant.user_id == payload.user_id).first()
    if existing:
        return existing
    participant = DiscussionParticipant(discussion_id=discussion_id, user_id=payload.user_id)
    db.add(participant)
    db.commit()
    db.refresh(participant)
    communication_service.create_discussion_notification(db, [payload.user_id], discussion)
    record_activity_log(db, current_user.id, "DISCUSSION_PARTICIPANT_ADDED", "Communication", "Discussion", discussion_id)
    return participant


@router.get("/{discussion_id}/participants", response_model=list[DiscussionParticipantOut])
def list_discussion_participants(discussion_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _get_accessible(db, discussion_id, current_user)
    return db.query(DiscussionParticipant).filter(DiscussionParticipant.discussion_id == discussion_id).order_by(DiscussionParticipant.joined_at.asc()).all()
