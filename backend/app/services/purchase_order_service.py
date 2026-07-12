from app.utils.constants import PROCUREMENT_STATUS_APPROVED


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
    return request_status == PROCUREMENT_STATUS_APPROVED and vendor_assigned