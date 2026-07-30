from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.auth import get_current_user, normalize_user_role
from app.core.database import get_db
from app.models.communication import Communication
from app.models.user import User
from app.schemas.communication import CommunicationCreate, CommunicationResponse

router = APIRouter(prefix="/communications", tags=["Communications"])

_COMMUNICATION_MANAGEMENT_ROLES = {
    "Administrator",
    "Procurement Manager",
    "Supply Chain Manager",
    "Auditor",
}


def _communications_query_for_user(db: Session, current_user: User):
    """Return only communication rows visible to the authenticated user."""
    query = db.query(Communication)
    role = normalize_user_role(current_user)
    if role in _COMMUNICATION_MANAGEMENT_ROLES:
        return query

    if role == "Vendor":
        from app.models.vendor import Vendor

        vendor = db.query(Vendor).filter(Vendor.email == current_user.email).first()
        if vendor:
            return query.filter(
                or_(Communication.sender_id == current_user.id, Communication.vendor_id == vendor.id)
            )

    return query.filter(Communication.sender_id == current_user.id)


@router.post("/", response_model=CommunicationResponse)
def create_communication(
    payload: CommunicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    values = payload.model_dump(exclude={"sender_id"})
    communication = Communication(**values, sender_id=current_user.id)
    db.add(communication)
    db.commit()
    db.refresh(communication)
    return communication


@router.get("/", response_model=List[CommunicationResponse])
def list_communications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _communications_query_for_user(db, current_user).order_by(Communication.created_at.desc()).all()


@router.get("/{communication_id}", response_model=CommunicationResponse)
def get_communication(
    communication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    communication = _communications_query_for_user(db, current_user).filter(
        Communication.id == communication_id
    ).first()
    if not communication:
        raise HTTPException(status_code=404, detail="Communication not found")
    return communication
