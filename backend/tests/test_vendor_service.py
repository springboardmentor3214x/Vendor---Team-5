from app.services.vendor_service import (
    can_vendor_be_assigned_to_procurement,
    validate_vendor_document,
    validate_unique_vendor_fields
)


def test_vendor_can_be_assigned_when_approved_and_active():
    assert can_vendor_be_assigned_to_procurement("approved", "active") is True


def test_vendor_cannot_be_assigned_when_pending():
    assert can_vendor_be_assigned_to_procurement("pending", "active") is False


def test_valid_vendor_document():
    assert validate_vendor_document("gst_certificate.pdf", 2) is True


def test_invalid_vendor_document_extension():
    assert validate_vendor_document("malware.exe", 2) is False


def test_duplicate_vendor_fields_invalid():
    assert validate_unique_vendor_fields(
        email_exists=True,
        gst_exists=False,
        pan_exists=False,
        registration_number_exists=False
    ) is False