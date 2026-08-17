"""HTTP regression coverage for communication record-level visibility."""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.auth import get_current_user
from app.core.database import get_db
from app.main import app
from app.models.communication_file import CommunicationFile
from app.models.discussion import Discussion
from app.models.discussion_participant import DiscussionParticipant


class _Query:
    def __init__(self, values):
        self.values = values

    def filter(self, *_predicates):
        return self

    def first(self):
        return self.values[0] if self.values else None


class _CommunicationAccessDb:
    def __init__(self):
        self.discussion = SimpleNamespace(
            id=7,
            vendor_id=None,
            purchase_order_id=None,
            contract_id=None,
            procurement_request_id=None,
        )
        self.file = SimpleNamespace(
            id=9,
            uploaded_by_id=101,
            discussion_id=None,
            vendor_id=None,
            purchase_order_id=None,
            contract_id=None,
            file_path="not-reached-forbidden-file",
        )

    def query(self, model):
        if model is Discussion:
            return _Query([self.discussion])
        if model is DiscussionParticipant:
            return _Query([])
        if model is CommunicationFile:
            return _Query([self.file])
        return _Query([])


@pytest.fixture
def non_participant_client():
    user = SimpleNamespace(id=202, email="outside@example.test", role="Vendor", is_active=True)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: _CommunicationAccessDb()
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


def test_non_participant_cannot_view_discussion(non_participant_client):
    response = non_participant_client.get("/communications/discussions/7")
    assert response.status_code == 403, response.text


def test_unlinked_user_cannot_download_communication_file(non_participant_client):
    response = non_participant_client.get("/communications/files/9/download")
    assert response.status_code == 403, response.text


@pytest.mark.parametrize(
    ("filename", "contents", "expected_status"),
    [
        ("not-allowed.exe", b"x", 415),
        ("too-large.pdf", b"x" * (10 * 1024 * 1024 + 1), 413),
    ],
    ids=["disallowed_type", "oversized_file"],
)
def test_communication_upload_enforces_type_and_size_limits(non_participant_client, filename, contents, expected_status):
    response = non_participant_client.post(
        "/communications/files/upload",
        files={"file": (filename, contents, "application/octet-stream")},
    )
    assert response.status_code == expected_status, response.text
