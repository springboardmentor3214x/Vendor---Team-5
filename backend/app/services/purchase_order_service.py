from datetime import date

from app.utils.constants import (
    PROCUREMENT_REQUEST_STATUS_APPROVED,
    PURCHASE_ORDER_STATUS_DRAFT,
    PURCHASE_ORDER_STATUS_ISSUED,
    PURCHASE_ORDER_STATUS_DELIVERED,
    PURCHASE_ORDER_STATUS_CANCELLED,
    ROLE_ADMIN,
    ROLE_PROCUREMENT_MANAGER
)


def generate_purchase_order_number(sequence_number: int) -> str:
    """
    Generate purchase order number automatically.
    Example: PO-2026-0001
    """
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
    comparison_date = actual_delivery_date or date.today()
    return comparison_date > expected_delivery_date


def can_complete_procurement(po_status: str, invoice_verified: bool) -> bool:
    """Return whether delivered goods have a verified invoice."""
    return po_status == PURCHASE_ORDER_STATUS_DELIVERED and invoice_verified


def can_user_update_purchase_order(user_role: str) -> bool:
    """Return whether the user can update purchase order status."""
    return user_role in [ROLE_ADMIN, ROLE_PROCUREMENT_MANAGER]
