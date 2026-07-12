from app.services.purchase_order_service import (
    generate_purchase_order_number,
    calculate_total_cost,
    can_create_purchase_order
)


def test_generate_purchase_order_number():
    assert generate_purchase_order_number(1) == "PO-2026-0001"


def test_calculate_total_cost():
    assert calculate_total_cost(10, 100, 180) == 1180


def test_can_create_purchase_order():
    assert can_create_purchase_order("approved", True) is True


def test_cannot_create_purchase_order_without_vendor():
    assert can_create_purchase_order("approved", False) is False