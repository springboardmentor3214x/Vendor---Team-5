"""HTTP coverage for the dedicated Module 7 direct-message API."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.auth import get_current_user
from app.core.database import Base, get_db
from app.main import app
from app.models.message import Message
from app.models.notification import Notification
from app.models.purchase_order import PurchaseOrder
from app.models.user import User
from app.models.vendor import Vendor
from app.models.vendor_category import VendorCategory
from app.services import notification_service


@pytest.fixture
def message_client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    sender = User(full_name="Sender User", email="sender@example.test", hashed_password="x", role="Administrator")
    receiver = User(full_name="Receiver User", email="receiver@example.test", hashed_password="x", role="Procurement Manager")
    vendor_user = User(full_name="Other Vendor", email="vendor@example.test", hashed_password="x", role="Vendor")
    session.add_all([sender, receiver, vendor_user])
    session.commit()
    state = {"user": sender}

    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: state["user"]
    monkeypatch.setattr(notification_service, "create_notification", lambda **kwargs: SimpleNamespace(**kwargs))
    try:
        with TestClient(app) as client:
            yield client, session, state, sender, receiver, vendor_user
    finally:
        app.dependency_overrides.clear()
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_send_message_uses_jwt_sender_and_ignores_spoofed_sender(message_client):
    client, session, _state, sender, receiver, _vendor = message_client
    response = client.post(
        "/messages",
        json={"receiverId": receiver.id, "senderId": 999999, "content": "Please review this."},
    )
    assert response.status_code == 201, response.text
    assert response.json()["senderId"] == sender.id
    assert response.json()["receiverId"] == receiver.id
    assert session.query(Message).one().sender_id == sender.id
    notification = session.query(Notification).one()
    assert notification.user_id == receiver.id
    assert notification.related_record_id == response.json()["id"]
    assert notification.related_module == "Messages"


def test_only_receiver_can_mark_message_read_and_unread_count_updates(message_client):
    client, _session, state, sender, receiver, _vendor = message_client
    created = client.post("/messages", json={"receiverId": receiver.id, "content": "New PO update"})
    message_id = created.json()["id"]

    assert client.get("/messages/unread-count").json()["unread"] == 0
    assert client.patch(f"/messages/{message_id}/read").status_code == 403

    state["user"] = receiver
    assert client.get("/messages/unread-count").json()["unread"] == 1
    marked = client.patch(f"/messages/{message_id}/read")
    assert marked.status_code == 200
    assert marked.json()["isRead"] is True
    assert client.get("/messages/unread-count").json()["unread"] == 0
    assert marked.json()["senderId"] == sender.id


def test_vendor_cannot_send_about_another_vendor_record(message_client):
    client, session, state, _sender, receiver, vendor_user = message_client
    category = VendorCategory(name="Demo category")
    session.add(category)
    session.commit()
    own_vendor = Vendor(
        company_name="Own Vendor",
        category_id=category.id,
        contact_person_name="Own Contact",
        email=vendor_user.email,
        phone_number="9999999999",
    )
    other_vendor = Vendor(
        company_name="Other Vendor",
        category_id=category.id,
        contact_person_name="Other Contact",
        email="other-vendor@example.test",
        phone_number="8888888888",
    )
    session.add_all([own_vendor, other_vendor])
    session.commit()
    state["user"] = vendor_user

    response = client.post(
        "/messages",
        json={
            "receiverId": receiver.id,
            "content": "I should not access this vendor.",
            "relatedEntityType": "vendor",
            "relatedEntityId": other_vendor.id,
        },
    )
    assert response.status_code == 403, response.text


def test_vendor_cannot_send_about_another_vendors_purchase_order(message_client):
    client, session, state, _sender, receiver, vendor_user = message_client
    category = VendorCategory(name="PO category")
    session.add(category)
    session.commit()
    own_vendor = Vendor(
        company_name="Own PO Vendor", category_id=category.id, contact_person_name="Own",
        email=vendor_user.email, phone_number="7777777777",
    )
    other_vendor = Vendor(
        company_name="Other PO Vendor", category_id=category.id, contact_person_name="Other",
        email="po-other@example.test", phone_number="6666666666",
    )
    session.add_all([own_vendor, other_vendor])
    session.commit()
    po = PurchaseOrder(
        procurement_request_id=9001,
        vendor_id=other_vendor.id,
        po_number="PO-MESSAGE-1",
    )
    session.add(po)
    session.commit()
    state["user"] = vendor_user

    response = client.post(
        "/messages",
        json={
            "receiverId": receiver.id,
            "content": "Unauthorized PO message",
            "relatedEntityType": "purchase_order",
            "relatedEntityId": po.id,
        },
    )
    assert response.status_code == 403, response.text


def test_context_contact_lookup_returns_only_real_related_users(message_client):
    client, session, state, sender, _receiver, vendor_user = message_client
    category = VendorCategory(name="Contact category")
    session.add(category)
    session.commit()
    vendor = Vendor(
        company_name="Message Contact Vendor", category_id=category.id,
        contact_person_name="Vendor Contact", email=vendor_user.email, phone_number="5555555555",
    )
    session.add(vendor)
    session.commit()

    state["user"] = sender
    response = client.get(
        "/messages/contacts",
        params={"relatedEntityType": "vendor", "relatedEntityId": vendor.id},
    )
    assert response.status_code == 200, response.text
    assert response.json() == [{
        "userId": vendor_user.id,
        "fullName": vendor_user.full_name,
        "email": vendor_user.email,
        "role": "Vendor",
    }]


def test_context_message_requires_receiver_to_participate_in_record(message_client):
    client, session, state, sender, receiver, vendor_user = message_client
    category = VendorCategory(name="Participant category")
    session.add(category)
    session.commit()
    vendor = Vendor(
        company_name="Participant Vendor", category_id=category.id,
        contact_person_name="Vendor Contact", email=vendor_user.email, phone_number="4444444444",
    )
    session.add(vendor)
    session.commit()
    state["user"] = sender

    response = client.post(
        "/messages",
        json={
            "receiverId": receiver.id,
            "content": "This user is unrelated to the vendor record.",
            "relatedEntityType": "vendor",
            "relatedEntityId": vendor.id,
        },
    )
    assert response.status_code == 403, response.text
