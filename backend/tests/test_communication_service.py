from types import SimpleNamespace

import pytest

from app.services.communication_service import (
    can_access_communication, create_discussion, get_contract_communication_history,
    get_conversation, get_vendor_communication_history, save_communication_file,
    send_message, validate_safe_file_name,
)
from app.models.communication import Communication
from app.models.discussion import Discussion
from app.models.discussion_participant import DiscussionParticipant


class Db:
    """Small persistence double for migrated Module 7 ORM rows."""
    def __init__(self):
        self.added = []
        self._next_id = 1

    def add(self, item):
        if getattr(item, "id", None) is None:
            item.id = self._next_id
            self._next_id += 1
        self.added.append(item)

    def commit(self):
        pass

    def refresh(self, item):
        pass

    def rollback(self):
        pass


def test_send_message_requires_db_session_and_persists_with_receiver_id():
    with pytest.raises(ValueError, match="database session"):
        send_message(None, 1, receiver_id=2, content="Hello")

    db = Db()
    result = send_message(db, 1, receiver_id=2, content="Hello")
    assert isinstance(result, Communication)
    assert result.receiver_id == 2
    assert result.sender_id == 1
    assert result.message == "Hello"
    assert any(isinstance(row, Communication) and row.receiver_id == 2 for row in db.added)
    with pytest.raises(ValueError, match="content"):
        send_message(None, 1, content=" ")


def test_create_discussion_requires_db_session_and_persists_participants():
    with pytest.raises(AttributeError):
        create_discussion(None, 1, "Pricing", [2])

    db = Db()
    discussion = create_discussion(db, 1, "Pricing", [2, 3])
    assert isinstance(discussion, Discussion)
    assert discussion.title == "Pricing"
    assert discussion.created_by_id == 1
    participants = [row for row in db.added if isinstance(row, DiscussionParticipant)]
    assert {row.user_id for row in participants} == {1, 2, 3}
    assert {row.discussion_id for row in participants} == {discussion.id}

    assert get_contract_communication_history(None, 4) == []
    with pytest.raises(ValueError, match="database session"):
        save_communication_file(None, "quote.pdf")
    assert validate_safe_file_name("quote.pdf") == "quote.pdf"
    with pytest.raises(ValueError):
        validate_safe_file_name("../quote.pdf")


def test_history_and_conversation_helpers_do_not_fabricate_data():
    assert get_vendor_communication_history(None, 7) == []
    assert get_conversation(None, 1, 2) == []


def test_access_control_respects_roles_participants_and_vendor_ownership():
    row = SimpleNamespace(sender_id=10, vendor_id=6, procurement_request_id=None, participant_ids=[12])
    assert can_access_communication({"id": 1, "role": "Administrator"}, row)
    assert can_access_communication({"id": 1, "role": "Auditor"}, row)
    assert can_access_communication({"id": 10, "role": "Vendor"}, row)
    assert can_access_communication({"id": 11, "role": "Vendor", "vendor_id": 6}, row)
    assert can_access_communication({"id": 12, "role": "Vendor"}, row)
    assert can_access_communication({"id": 14, "role": "Finance Officer"}, row)
    assert not can_access_communication({"id": 13, "role": "Vendor"}, row)
