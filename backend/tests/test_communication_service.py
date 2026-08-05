from types import SimpleNamespace

import pytest

from app.services.communication_service import (
    can_access_communication, create_discussion, get_contract_communication_history,
    get_conversation, get_vendor_communication_history, save_communication_file,
    send_message, validate_safe_file_name,
)


class _Db:
    """Minimal unit-test session that exercises persisted Module 7 models."""

    def __init__(self):
        self.added = []

    def add(self, item):
        self.added.append(item)

    def commit(self):
        pass

    def refresh(self, item):
        if getattr(item, "id", None) is None:
            item.id = len(self.added)

    def rollback(self):
        pass


def test_send_message_requires_session_and_persists_receiver_id():
    result = send_message(None, 1, receiver_id=2, content="Hello")
    assert result["status"] == "unavailable"
    assert "database session" in result["message"].lower()

    db = _Db()
    message = send_message(db, 1, receiver_id=2, content="Hello")
    assert message.sender_id == 1
    assert message.receiver_id == 2
    assert message.message == "Hello"
    assert message in db.added
    with pytest.raises(ValueError, match="content"):
        send_message(None, 1, content=" ")


def test_create_discussion_requires_session_and_persists_participants():
    unavailable = create_discussion(None, 1, "Pricing", [2])
    assert unavailable["status"] == "unavailable"
    assert "persistence" in unavailable["message"].lower()

    db = _Db()
    discussion = create_discussion(db, 1, "Pricing", [2, 3])
    assert discussion.title == "Pricing"
    assert discussion.created_by_id == 1
    participants = [item for item in db.added if hasattr(item, "discussion_id") and hasattr(item, "user_id")]
    assert {(item.discussion_id, item.user_id) for item in participants} == {(discussion.id, 1), (discussion.id, 2), (discussion.id, 3)}


def test_file_and_history_helpers_handle_missing_session_without_fabricating_records():
    res = get_contract_communication_history(None, 4)
    assert res == [] or (isinstance(res, dict) and res.get("status") == "unavailable")
    assert save_communication_file(None, "quote.pdf")["status"] == "unavailable"
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
