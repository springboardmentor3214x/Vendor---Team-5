"""Persistence helpers for dedicated one-to-one Module 7 messages.

This deliberately does not replace the existing procurement Communication or
Discussion services.  It serves the separate direct-message workspace only.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.message import Message, RelatedEntityType
from app.models.user import User


def send_message(
    db: Session,
    *,
    sender_id: int,
    receiver_id: int,
    content: str,
    related_entity_type: RelatedEntityType = RelatedEntityType.NONE,
    related_entity_id: Optional[int] = None,
) -> Message:
    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content.strip(),
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        is_read=False,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_conversation(
    db: Session,
    *,
    user_a_id: int,
    user_b_id: int,
    related_entity_type: Optional[RelatedEntityType] = None,
    related_entity_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Message]:
    query = db.query(Message).filter(
        or_(
            and_(Message.sender_id == user_a_id, Message.receiver_id == user_b_id),
            and_(Message.sender_id == user_b_id, Message.receiver_id == user_a_id),
        )
    )
    if related_entity_type is not None:
        query = query.filter(Message.related_entity_type == related_entity_type)
    if related_entity_id is not None:
        query = query.filter(Message.related_entity_id == related_entity_id)
    return query.order_by(Message.created_at.asc(), Message.id.asc()).offset(offset).limit(limit).all()


def list_conversations(db: Session, *, user_id: int, limit: int = 50, offset: int = 0) -> list[dict]:
    """Return one current summary per counterpart without DB-specific SQL."""
    messages = (
        db.query(Message)
        .filter(or_(Message.sender_id == user_id, Message.receiver_id == user_id))
        .order_by(Message.created_at.desc(), Message.id.desc())
        .all()
    )

    summaries: dict[int, dict] = {}
    for message in messages:
        counterpart_id = message.receiver_id if message.sender_id == user_id else message.sender_id
        summary = summaries.get(counterpart_id)
        if summary is None:
            counterpart = db.query(User).filter(User.id == counterpart_id).first()
            summary = {
                "counterpart_user_id": counterpart_id,
                "counterpart_name": getattr(counterpart, "full_name", None),
                "counterpart_email": getattr(counterpart, "email", None),
                "last_message_content": message.content,
                "last_message_at": message.created_at,
                "unread_count": 0,
                "related_entity_type": message.related_entity_type,
                "related_entity_id": message.related_entity_id,
            }
            summaries[counterpart_id] = summary
        if message.receiver_id == user_id and not message.is_read:
            summary["unread_count"] += 1

    ordered = sorted(summaries.values(), key=lambda item: item["last_message_at"] or datetime.min, reverse=True)
    return ordered[offset : offset + limit]


def mark_as_read(db: Session, *, message_id: int, reader_id: int) -> Optional[Message]:
    message = db.query(Message).filter(Message.id == message_id).first()
    if message is None or message.receiver_id != reader_id:
        return None
    if not message.is_read:
        message.is_read = True
        message.read_at = datetime.utcnow()
        db.commit()
        db.refresh(message)
    return message


def get_unread_count(db: Session, *, user_id: int) -> int:
    return db.query(Message).filter(Message.receiver_id == user_id, Message.is_read == False).count()
