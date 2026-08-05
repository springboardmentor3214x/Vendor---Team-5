from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from app.models.certification import Certification
from app.models.contract import Contract
from app.models.purchase_order import PurchaseOrder
from app.services.notification_service import (
    build_email_notification_payload, build_sms_notification_payload, classify_notification_priority,
    create_notification, generate_compliance_expiry_notifications, generate_contract_expiry_notifications,
    generate_procurement_alert, get_notification_summary, get_unread_notifications, get_user_notifications,
    mark_all_notifications_read, mark_notification_as_read, scan_for_pending_notifications,
    send_email_notification, send_sms_notification,
)


def test_notification_model_absence_returns_no_fabricated_records():
    assert get_user_notifications(None, 7) == []
    assert get_unread_notifications(None, 7) == []
    assert mark_notification_as_read(None, 1, 7) is None
    result = create_notification(None, 7, "Title", "Message")
    assert result["status"] == "unavailable"


def test_external_delivery_helpers_are_safe_structured_placeholders():
    assert send_email_notification("recipient@example.com", "subject", "body") == {
        "status": "placeholder", "channel": "email", "message": "Email delivery is not configured.",
    }
    assert send_sms_notification("+919999999999", "body") == {
        "status": "placeholder", "channel": "sms", "message": "SMS delivery is not configured.",
    }


def test_priority_payloads_and_validation_are_deterministic_without_external_delivery():
    assert classify_notification_priority("critical_delivery_delay") == "high"
    assert classify_notification_priority("vendor_approved") == "medium"
    assert classify_notification_priority("new_message_received") == "low"
    notification = {"id": 4, "title": "PO delayed", "message": "PO-4 is delayed"}
    assert build_email_notification_payload(notification, {"email": "user@example.com"})["to"] == "user@example.com"
    assert build_sms_notification_payload(notification, "+919999999999")["channel"] == "sms"
    with pytest.raises(ValueError, match="user_id"):
        create_notification(None, 0, "Title", "Description")
    with pytest.raises(ValueError, match="description"):
        create_notification(None, 1, "Title", " ")


class Query:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class Db:
    def __init__(self, rows):
        self.rows = rows

    def query(self, model):
        return Query(self.rows.get(model, []))


def test_expiry_and_scheduled_scans_report_real_matches_but_no_fake_persistence():
    expiry = date.today() + timedelta(days=7)
    db = Db({Contract: [SimpleNamespace(id=1, end_date=expiry)],
             Certification: [SimpleNamespace(id=2, expiry_date=expiry)],
             PurchaseOrder: [SimpleNamespace(id=3, expected_delivery_date=date.today() - timedelta(days=1), po_status="Issued", created_by=9)]})
    assert generate_contract_expiry_notifications(db)["matched_entity_ids"] == [1]
    assert generate_compliance_expiry_notifications(db)["matched_entity_ids"] == [2]
    scan = scan_for_pending_notifications(db)
    assert scan["delivery_delay"][0]["status"] == "unavailable"
    with pytest.raises(ValueError, match="Unsupported procurement"):
        generate_procurement_alert(db, 1, "bad")
    assert mark_all_notifications_read(None, 1) == 0
    assert get_notification_summary(None, 1) == {"total_notifications": 0, "unread_count": 0,
                                                   "high_priority_count": 0, "recent_notifications": []}
