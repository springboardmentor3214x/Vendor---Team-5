from app.services.invoice_service import (
    calculate_invoice_total,
    can_verify_invoice,
    verify_invoice,
    approve_payment,
    mark_invoice_paid,
    reject_invoice
)


def test_calculate_invoice_total():
    assert calculate_invoice_total(1000, 180) == 1180


def test_finance_officer_can_verify_invoice():
    assert can_verify_invoice("Finance Officer") is True


def test_verify_invoice():
    assert verify_invoice("pending", "Finance Officer") == "verified"


def test_approve_payment():
    assert approve_payment("verified", "Finance Officer") == "approved"


def test_mark_invoice_paid():
    assert mark_invoice_paid("approved") == "paid"


def test_reject_invoice():
    assert reject_invoice("pending", "Finance Officer") == "rejected"