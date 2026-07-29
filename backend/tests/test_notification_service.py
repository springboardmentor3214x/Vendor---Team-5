from app.services.notification_service import (
    create_notification, get_unread_notifications, get_user_notifications,
    mark_notification_as_read, send_email_notification, send_sms_notification,
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
