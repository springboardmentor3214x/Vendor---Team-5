import enum
from datetime import datetime
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Index, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class RelatedEntityType(str, enum.Enum):
    VENDOR = "vendor"
    PROCUREMENT_REQUEST = "procurement_request"
    PURCHASE_ORDER = "purchase_order"
    CONTRACT = "contract"
    NONE = "none"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    related_entity_type = Column(
        SQLEnum(
            RelatedEntityType,
            name="related_entity_type",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=RelatedEntityType.NONE,
        server_default="none",
    )
    related_entity_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())
    read_at = Column(DateTime, nullable=True)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

    __table_args__ = (
        Index("ix_messages_sender_id_created_at", "sender_id", "created_at"),
        Index("ix_messages_receiver_id_is_read_created_at", "receiver_id", "is_read", "created_at"),
    )
