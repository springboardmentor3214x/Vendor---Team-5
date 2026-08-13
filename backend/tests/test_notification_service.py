from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import pytest

from app.services.notification_service import (
    create_notification,
    get_unread_notifications,
    get_user_notifications,
    mark_notification_as_read,
    mark_all_user_notifications_as_read,
    send_email_notification,
    send_sms_notification,
    create_vendor_approval_notification,
    create_procurement_alert,
    create_delivery_delay_notification,
    trigger_contract_expiry_reminders,
    trigger_compliance_expiry_reminders,
    execute_all_background_notification_checks,
)
from app.models.notification import Notification
from app.models.contract import Contract
from app.models.vendor import Vendor
from app.models.purchase_order import PurchaseOrder
from app.models.user import User


def test_notification_creation_and_retrieval():
    db = MagicMock()
    mock_notif = Notification(
        id=1,
        user_id=10,
        title="PO Created",
        message="PO #101 created",
        notification_type="PROCUREMENT_ALERT",
        priority="HIGH",
        is_read=False
    )
    db.query().filter().order_by().all.return_value = [mock_notif]

    res = get_user_notifications(db=db, user_id=10)
    assert len(res) == 1
    assert res[0].title == "PO Created"
    assert res[0].priority == "HIGH"


def test_mark_notification_as_read():
    db = MagicMock()
    mock_notif = Notification(id=1, user_id=10, is_read=False, read_at=None)
    db.query().filter().first.return_value = mock_notif

    res = mark_notification_as_read(db=db, notification_id=1, user_id=10)
    assert res is not None
    assert res.is_read is True
    assert res.read_at is not None
    assert db.commit.called


def test_mark_all_user_notifications_as_read():
    db = MagicMock()
    n1 = Notification(id=1, user_id=10, is_read=False)
    n2 = Notification(id=2, user_id=10, is_read=False)
    db.query().filter().order_by().all.return_value = [n1, n2]

    count = mark_all_user_notifications_as_read(db=db, user_id=10)
    assert count == 2
    assert n1.is_read is True
    assert n2.is_read is True
    assert db.commit.called


def test_email_and_sms_notification_helpers():
    email_res = send_email_notification("user@vendoriq.com", "Test Subject", "Test Body")
    assert email_res["status"] == "not_configured"
    assert email_res["channel"] == "email"

    sms_res = send_sms_notification("+919876543210", "Test SMS")
    assert sms_res["status"] == "not_configured"
    assert sms_res["channel"] == "sms"


def test_email_and_sms_send_only_with_complete_configuration(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.test")
    monkeypatch.setenv("SMTP_USERNAME", "mailer@example.test")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    with patch("app.services.notification_service.smtplib.SMTP") as smtp:
        assert send_email_notification("user@example.test", "Subject", "Body")["status"] == "sent"
        assert smtp.called

    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "AC123")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "secret")
    monkeypatch.setenv("TWILIO_FROM_NUMBER", "+15551234567")
    with patch("app.services.notification_service.urlopen") as open_request:
        assert send_sms_notification("+15557654321", "Body")["status"] == "sent"
        assert open_request.called


def test_create_vendor_approval_notification():
    mock_vendor = Vendor(id=5, company_name="ABC Steel Pvt Ltd", email="vendor@abc.com")
    vendor_user = MagicMock(id=9, email="vendor@abc.com", is_active=True)

    class Query:
        def __init__(self, model): self.model = model
        def filter(self, *_): return self
        def first(self):
            if self.model is Vendor: return mock_vendor
            if self.model is User: return vendor_user
            return None
        def all(self): return [vendor_user] if self.model is User else []

    db = MagicMock()
    db.query.side_effect = Query

    notifs = create_vendor_approval_notification(db=db, vendor_id=5, approved=True)
    assert len(notifs) == 1
    assert "approved" in notifs[0].message
    assert notifs[0].priority == "MEDIUM"


def test_delivery_alert_targets_vendor_and_assigned_procurement_user_without_duplicates(monkeypatch):
    po = MagicMock(id=12, vendor_id=5, assigned_procurement_manager_id=3)
    vendor = MagicMock(id=5, email="vendor@example.test")
    users = [
        MagicMock(id=3, email="buyer@example.test", is_active=True),
        MagicMock(id=4, email="vendor@example.test", is_active=True),
        MagicMock(id=8, email="admin@example.test", is_active=True),
    ]

    class Query:
        def __init__(self, model): self.model = model
        def filter(self, *_): return self
        def first(self): return po if self.model is PurchaseOrder else vendor if self.model is Vendor else None
        def all(self): return users if self.model is User else []

    db = MagicMock()
    db.query.side_effect = Query
    created = []
    monkeypatch.setattr("app.services.notification_service.create_notification", lambda **payload: created.append(payload) or MagicMock(**payload))
    monkeypatch.setattr("app.services.notification_service._notification_exists_for_today", lambda *_args, **_kwargs: False)
    assert len(create_delivery_delay_notification(db, 12)) == 2
    assert {item["user_id"] for item in created} == {3, 4}

    monkeypatch.setattr("app.services.notification_service._notification_exists_for_today", lambda *_args, **_kwargs: True)
    assert create_delivery_delay_notification(db, 12) == []


def test_create_procurement_alert():
    db = MagicMock()
    alert = create_procurement_alert(db=db, user_id=2, pr_id=101, status="approval_required", pr_title="Raw Steel")
    assert alert.title == "Procurement Request: APPROVAL_REQUIRED"
    assert alert.priority == "HIGH"


def test_background_notification_checks():
    db = MagicMock()
    db.query().all.return_value = []

    res = execute_all_background_notification_checks(db=db)
    assert res["status"] == "success"
    assert "contract_expiry_alerts_generated" in res
    assert "delivery_delay_alerts_generated" in res
    assert "compliance_expiry_alerts_generated" in res
