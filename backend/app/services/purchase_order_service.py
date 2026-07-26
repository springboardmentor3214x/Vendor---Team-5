from datetime import date

from app.utils.constants import (
    PROCUREMENT_REQUEST_STATUS_APPROVED,
    PURCHASE_ORDER_STATUS_DRAFT,
    PURCHASE_ORDER_STATUS_ISSUED,
    PURCHASE_ORDER_STATUS_DELIVERED,
    PURCHASE_ORDER_STATUS_COMPLETED,
    PURCHASE_ORDER_STATUS_CANCELLED,
    ROLE_ADMIN,
    ROLE_PROCUREMENT_MANAGER,
    INVOICE_STATUS_VERIFIED,
    INVOICE_STATUS_APPROVED,
    INVOICE_STATUS_PAID,
)


def generate_purchase_order_number(sequence_number: int) -> str:
    """
    Generate purchase order number automatically.
    Example: PO-2026-0001
    """
    _validate_sequence_number(sequence_number)
    return f"PO-2026-{sequence_number:04d}"


def calculate_total_cost(
    quantity: int,
    unit_price: float,
    tax_amount: float = 0
) -> float:
    """
    Calculate total purchase order cost.
    """
    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    if unit_price < 0:
        raise ValueError("Unit price cannot be negative")

    if tax_amount < 0:
        raise ValueError("Tax amount cannot be negative")

    total = quantity * unit_price + tax_amount
    return round(total, 2)


def can_create_purchase_order(
    request_status: str,
    vendor_assigned: bool
) -> bool:
    """
    Purchase order can be created only after procurement request approval
    and vendor assignment.
    """
    return (
        request_status == PROCUREMENT_REQUEST_STATUS_APPROVED
        and vendor_assigned
    )


def issue_purchase_order(current_status: str) -> str:
    """Issue a purchase order if it is in draft status."""
    if current_status != PURCHASE_ORDER_STATUS_DRAFT:
        raise ValueError("Only draft purchase orders can be issued")

    return PURCHASE_ORDER_STATUS_ISSUED


def mark_purchase_order_delivered(current_status: str) -> str:
    """Mark an issued purchase order as delivered."""
    if current_status != PURCHASE_ORDER_STATUS_ISSUED:
        raise ValueError("Only issued purchase orders can be marked delivered")

    return PURCHASE_ORDER_STATUS_DELIVERED


def cancel_purchase_order(current_status: str) -> str:
    """Cancel a draft or issued purchase order."""
    if current_status not in [
        PURCHASE_ORDER_STATUS_DRAFT,
        PURCHASE_ORDER_STATUS_ISSUED
    ]:
        raise ValueError("Only draft or issued purchase orders can be cancelled")

    return PURCHASE_ORDER_STATUS_CANCELLED


def is_delivery_delayed(
    expected_delivery_date: date,
    actual_delivery_date: date | None = None
) -> bool:
    """Return whether the delivery date is later than the expected date."""
    if expected_delivery_date is None:
        raise ValueError("Expected delivery date is required")
    comparison_date = actual_delivery_date or date.today()
    return comparison_date > expected_delivery_date


def can_complete_procurement(po_status: str, invoice_status: str) -> bool:
    """Return whether the PO and invoice have completion-eligible statuses."""
    normalized_invoice_status = invoice_status.casefold()
    return (
        po_status in {
            PURCHASE_ORDER_STATUS_DELIVERED,
            PURCHASE_ORDER_STATUS_COMPLETED,
        }
        and normalized_invoice_status in {
            INVOICE_STATUS_VERIFIED,
            INVOICE_STATUS_APPROVED,
            INVOICE_STATUS_PAID,
        }
    )


def can_complete_procurement_with_invoice_status(
    po_status: str,
    invoice_status: str,
) -> bool:
    """Compatibility alias for the status-aware procurement completion check."""
    return can_complete_procurement(po_status, invoice_status)


def can_user_update_purchase_order(user_role: str) -> bool:
    """Return whether the user can update purchase order status."""
    return user_role in [ROLE_ADMIN, ROLE_PROCUREMENT_MANAGER]


def _validate_sequence_number(sequence_number: int) -> None:
    if isinstance(sequence_number, bool) or not isinstance(sequence_number, int):
        raise ValueError("Sequence number must be a positive integer")
    if sequence_number <= 0:
        raise ValueError("Sequence number must be a positive integer")
