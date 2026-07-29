from app.utils.constants import (
    ROLE_ADMIN,
    ROLE_FINANCE_OFFICER,
    INVOICE_STATUS_PENDING,
    INVOICE_STATUS_VERIFIED,
    INVOICE_STATUS_APPROVED,
    INVOICE_STATUS_PAID,
    INVOICE_STATUS_REJECTED
)


def calculate_invoice_total(
    invoice_amount: float,
    tax_amount: float = 0
) -> float:
    """
    Calculate invoice total amount.
    """
    if invoice_amount < 0:
        raise ValueError("Invoice amount cannot be negative")

    if tax_amount < 0:
        raise ValueError("Tax amount cannot be negative")

    return round(invoice_amount + tax_amount, 2)


def can_verify_invoice(user_role: str) -> bool:
    """
    Only Finance Officer and Admin can verify invoices.
    """
    return user_role in [ROLE_FINANCE_OFFICER, ROLE_ADMIN]


def verify_invoice(current_status: str, user_role: str) -> str:
    """
    Verify invoice if user has finance permission.
    """
    if not can_verify_invoice(user_role):
        raise PermissionError("Only Finance Officer or Admin can verify invoice")

    if current_status != INVOICE_STATUS_PENDING:
        raise ValueError("Only pending invoices can be verified")

    return INVOICE_STATUS_VERIFIED


def approve_payment(current_status: str, user_role: str) -> str:
    """
    Approve payment after invoice verification.
    """
    if not can_verify_invoice(user_role):
        raise PermissionError("Only Finance Officer or Admin can approve payment")

    if current_status != INVOICE_STATUS_VERIFIED:
        raise ValueError("Only verified invoices can be approved for payment")

    return INVOICE_STATUS_APPROVED


def mark_invoice_paid(current_status: str) -> str:
    """
    Mark invoice as paid after payment approval.
    """
    if current_status != INVOICE_STATUS_APPROVED:
        raise ValueError("Only approved invoices can be marked as paid")

    return INVOICE_STATUS_PAID


def reject_invoice(current_status: str, user_role: str) -> str:
    """
    Reject invoice if it is pending or verified.
    """
    if not can_verify_invoice(user_role):
        raise PermissionError("Only Finance Officer or Admin can reject invoice")

    if current_status not in [INVOICE_STATUS_PENDING, INVOICE_STATUS_VERIFIED]:
        raise ValueError("Only pending or verified invoices can be rejected")

    return INVOICE_STATUS_REJECTED
