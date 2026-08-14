import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

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


def prepare_purchase_order_print_data(purchase_order: object, request: object, vendor: object) -> dict:
    """Return a PDF/print-ready PO payload exclusively from persisted PO, request and vendor rows."""
    if purchase_order is None or request is None or vendor is None:
        raise ValueError("Purchase order, procurement request, and vendor data are required")
    quantity = getattr(purchase_order, "quantity", None)
    unit_price = getattr(purchase_order, "unit_price", None)
    total_cost = getattr(purchase_order, "total_cost", None)
    return {
        "purchase_order": {key: getattr(purchase_order, key, None) for key in (
            "id", "po_number", "po_date", "po_status", "quantity", "unit_price", "total_cost", "tax_details",
            "shipping_address", "expected_delivery_date", "actual_delivery_date", "payment_terms", "project_name")},
        "request": {key: getattr(request, key, None) for key in (
            "id", "request_number", "title", "department", "project_name", "item_description", "product_name",
            "product_category", "quantity", "unit_of_measurement", "business_justification", "required_delivery_date")},
        "vendor": {key: getattr(vendor, key, None) for key in (
            "id", "company_name", "contact_person_name", "email", "phone_number", "address_line1", "address_line2",
            "city", "state", "country", "pincode", "gst_number", "pan_number")},
        "line_items": [{"description": getattr(request, "item_description", None) or getattr(request, "product_name", None),
                        "quantity": quantity, "unit_price": unit_price, "line_total": total_cost}],
    }


def render_purchase_order_pdf(purchase_order: object, request: object, vendor: object) -> bytes:
    """Render the persisted PO data as a downloadable, print-ready PDF."""
    data = prepare_purchase_order_print_data(purchase_order, request, vendor)
    po, request_data, vendor_data = data["purchase_order"], data["request"], data["vendor"]
    output, styles = io.BytesIO(), getSampleStyleSheet()
    story = [Paragraph("Purchase Order", styles["Title"]),
             Paragraph(f"PO Number: {po.get('po_number') or po.get('id')}", styles["Heading2"]), Spacer(1, 0.15 * inch)]
    details = [
        ["Vendor", vendor_data.get("company_name") or "-"], ["Contact", vendor_data.get("contact_person_name") or "-"],
        ["Request", request_data.get("request_number") or request_data.get("title") or "-"],
        ["Status", po.get("po_status") or "-"], ["Delivery date", str(po.get("expected_delivery_date") or "-")],
        ["Payment terms", po.get("payment_terms") or "-"],
    ]
    details_table = Table(details, colWidths=[1.5 * inch, 5.7 * inch])
    details_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF2F8")),
                                       ("GRID", (0, 0), (-1, -1), 0.25, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.extend([details_table, Spacer(1, 0.2 * inch)])
    items = [["Description", "Quantity", "Unit price", "Line total"]]
    for item in data["line_items"]:
        items.append([str(item.get("description") or "-"), str(item.get("quantity") or "-"),
                      str(item.get("unit_price") or "-"), str(item.get("line_total") or "-")])
    item_table = Table(items, colWidths=[3.5 * inch, 1 * inch, 1.2 * inch, 1.2 * inch], repeatRows=1)
    item_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                                    ("ALIGN", (1, 1), (-1, -1), "RIGHT")]))
    story.append(item_table)
    SimpleDocTemplate(output, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36).build(story)
    return output.getvalue()


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
