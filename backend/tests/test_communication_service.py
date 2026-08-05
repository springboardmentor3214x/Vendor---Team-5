from types import SimpleNamespace

import pytest

from app.services.communication_service import (
    can_access_communication, create_discussion, get_contract_communication_history,
    get_conversation, get_vendor_communication_history, save_communication_file,
    send_message, validate_safe_file_name,
)


def test_message_persistence_requires_receiver_schema_for_direct_messages():
    result = send_message(None, 1, receiver_id=2, content="Hello")
    assert result["status"] == "unavailable"
    with pytest.raises(ValueError, match="content"):
        send_message(None, 1, content=" ")


def test_unmigrated_discussion_file_and_contract_features_are_explicit():
    assert create_discussion(None, 1, "Pricing", [2])["status"] == "unavailable"
    assert get_contract_communication_history(None, 4)["status"] == "unavailable"
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
