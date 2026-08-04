import os
from unittest.mock import MagicMock
from datetime import datetime
import pytest

from app.services import communication_service, discussion_service, activity_log_service
from app.schemas.communication import CommunicationCreate, DiscussionCreate
from app.models.communication import Communication
from app.models.discussion import Discussion
from app.models.activity_log import ActivityLog
from app.models.communication_file import CommunicationFile


def test_send_message():
    db = MagicMock()
    payload = CommunicationCreate(
        sender_id=1,
        receiver_id=2,
        vendor_id=5,
        purchase_order_id=10,
        subject="PO Clarification",
        message="Please confirm delivery date.",
        message_type="DIRECT"
    )

    msg = communication_service.send_message(db=db, payload=payload, sender_user_id=1, ip_address="127.0.0.1")

    assert msg is not None
    assert msg.sender_id == 1
    assert msg.receiver_id == 2
    assert msg.vendor_id == 5
    assert msg.purchase_order_id == 10
    assert msg.message == "Please confirm delivery date."
    assert db.add.called
    assert db.commit.called


def test_mark_message_as_read():
    db = MagicMock()
    mock_msg = Communication(id=1, is_read=False, read_at=None)
    db.query().filter().first.return_value = mock_msg

    updated_msg = communication_service.mark_message_as_read(db=db, message_id=1, user_id=2)

    assert updated_msg.is_read is True
    assert updated_msg.read_at is not None
    assert db.commit.called


def test_create_discussion_thread():
    db = MagicMock()
    payload = DiscussionCreate(
        title="Schedule Negotiation",
        vendor_id=3,
        purchase_order_id=7,
        participant_user_ids=[2, 3],
        initial_message="Discussing revised timeline."
    )

    discussion = discussion_service.create_discussion_thread(
        db=db,
        payload=payload,
        creator_user_id=1,
        ip_address="192.168.1.1"
    )

    assert discussion is not None
    assert discussion.title == "Schedule Negotiation"
    assert discussion.status == "OPEN"
    assert db.add.called
    assert db.commit.called


def test_update_discussion_status():
    db = MagicMock()
    mock_discussion = Discussion(id=1, title="Test", status="OPEN", updated_at=datetime.utcnow())
    db.query().filter().first.return_value = mock_discussion

    res = discussion_service.update_discussion_status(db=db, discussion_id=1, status="RESOLVED", user_id=1)

    assert res.status == "RESOLVED"
    assert db.commit.called


def test_log_activity_and_query():
    db = MagicMock()

    log_entry = activity_log_service.log_activity(
        db=db,
        user_id=1,
        module="Communication",
        action="MESSAGE_SENT",
        description="Test log message",
        related_entity_type="Vendor",
        related_entity_id=5,
        ip_address="127.0.0.1"
    )

    assert log_entry is not None
    assert log_entry.module == "Communication"
    assert log_entry.action == "MESSAGE_SENT"
    assert log_entry.related_entity_id == 5
    assert db.add.called
    assert db.commit.called
