from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class DiscussionParticipant(Base):
    __tablename__ = "discussion_participants"

    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(Integer, ForeignKey("discussions.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    joined_at = Column(DateTime, default=datetime.utcnow, index=True)
