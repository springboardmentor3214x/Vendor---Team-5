from datetime import date, datetime

from app.services.performance_service import (
    calculate_average_communication_score,
    calculate_average_delivery_score,
    calculate_average_quality_score,
    calculate_average_response_time,
    calculate_average_score,
    calculate_average_service_rating_score,
    calculate_communication_score,
    calculate_delayed_delivery_count,
    calculate_delivery_delay,
    calculate_delivery_score,
    calculate_on_time_delivery_rate,
    calculate_on_time_delivery_rate_from_statuses,
    calculate_order_completion_rate,
    calculate_overall_performance_score,
    calculate_quality_score,
    calculate_response_duration_minutes,
    calculate_service_rating_score,
    generate_vendor_ranking,
    get_delivery_status,
    get_performance_status,
    can_recalculate_vendor_ranking,
    can_user_recalculate_vendor_ranking,
    recalculate_vendor_ranking,
    recalculate_vendor_ranking_after_performance_write,
    validate_no_duplicate_performance_entry,
    validate_performance_write_eligibility,
)
from app.models.performance import PerformanceRecord
from app.models.purchase_order import PurchaseOrder
import pytest


def test_calculate_delivery_delay():
    assert calculate_delivery_delay(date(2026, 1, 5), date(2026, 1, 7)) == 2


def test_get_delivery_statuses():
    assert get_delivery_status(date(2026, 1, 5), date(2026, 1, 4)) == "Early Delivery"
    assert get_delivery_status(date(2026, 1, 5), date(2026, 1, 5)) == "On-Time Delivery"
    assert get_delivery_status(date(2026, 1, 5), date(2026, 1, 6)) == "Delayed Delivery"


def test_calculate_delivery_score():
    assert calculate_delivery_score(0) == 100
    assert calculate_delivery_score(2) == 80
    assert calculate_delivery_score(5) == 60
    assert calculate_delivery_score(6) == 40


def test_calculate_quality_score_with_defect_penalty():
    assert calculate_quality_score(5, 4, 5, 4, product_defects=2) == 80


def test_calculate_response_duration_minutes():
    assert calculate_response_duration_minutes(
        datetime(2026, 1, 1, 10, 0),
        datetime(2026, 1, 1, 12, 30)
    ) == 150


def test_calculate_communication_score():
    assert calculate_communication_score(120) == 100
    assert calculate_communication_score(360) == 80
    assert calculate_communication_score(1440) == 60
    assert calculate_communication_score(1441) == 40


def test_calculate_service_rating_score():
    assert calculate_service_rating_score(5, 4, 3, 4, 5, 3) == 80


def test_calculate_overall_performance_score():
    assert calculate_overall_performance_score(100, 80, 60, 80) == 82


def test_get_performance_statuses():
    assert get_performance_status(80) == "Excellent"
    assert get_performance_status(60) == "Good"
    assert get_performance_status(40) == "Average"
    assert get_performance_status(39) == "Poor"


def test_calculate_on_time_delivery_rate():
    assert calculate_on_time_delivery_rate(3, 2) == 66.67
    assert calculate_on_time_delivery_rate(0, 0) == 0.0


def test_on_time_delivery_rate_from_statuses_counts_early_and_on_time_only():
    statuses = ["Early Delivery", "On-Time Delivery", "Delayed Delivery"]
    assert calculate_on_time_delivery_rate_from_statuses(statuses) == 66.67


def test_calculate_delayed_delivery_count():
    statuses = ["On-Time Delivery", "Delayed Delivery", "Delayed Delivery"]
    assert calculate_delayed_delivery_count(statuses) == 2


def test_calculate_average_delivery_score_is_distinct_from_on_time_delivery_rate():
    assert calculate_average_delivery_score([100, 80, 40]) == 73.33
    assert calculate_average_delivery_score([]) == 0.0


def test_calculate_average_score_returns_zero_for_an_empty_list():
    assert calculate_average_score([]) == 0


def test_calculate_average_score_returns_a_rounded_average():
    assert calculate_average_score([100, 80, 40]) == 73.33


def test_score_averages_do_not_use_the_response_time_helper(monkeypatch):
    def response_time_helper_used(_response_times):
        raise AssertionError("Response-time helper must only average durations")

    monkeypatch.setattr(
        "app.services.performance_service.calculate_average_response_time",
        response_time_helper_used,
    )

    assert calculate_average_delivery_score([100, 80, 40]) == 73.33
    assert calculate_average_communication_score([100, 80, 60]) == 80.0
    assert calculate_average_service_rating_score([100, 60, 80]) == 80.0


def test_calculate_average_quality_score():
    assert calculate_average_quality_score([80, 90, 85]) == 85.0
    assert calculate_average_quality_score([]) == 0.0


def test_calculate_average_response_time():
    assert calculate_average_response_time([30, 45, 60]) == 45.0
    assert calculate_average_response_time([]) == 0.0


def test_calculate_order_completion_rate():
    assert calculate_order_completion_rate(4, 3) == 75.0
    assert calculate_order_completion_rate(0, 0) == 0.0


def test_generate_vendor_ranking():
    vendor_scores = [
        {"vendor_id": 1, "vendor_name": "ABC", "overall_performance_score": 90},
        {"vendor_id": 2, "vendor_name": "XYZ", "overall_performance_score": 75}
    ]

    ranking = generate_vendor_ranking(vendor_scores)

    assert ranking == [
        {
            "vendor_id": 1,
            "vendor_name": "ABC",
            "overall_performance_score": 90,
            "rank_position": 1
        },
        {
            "vendor_id": 2,
            "vendor_name": "XYZ",
            "overall_performance_score": 75,
            "rank_position": 2
        }
    ]


def test_only_administrator_or_procurement_manager_can_recalculate_rankings():
    assert can_recalculate_vendor_ranking("Administrator") is True
    assert can_recalculate_vendor_ranking("Procurement Manager") is True
    assert can_recalculate_vendor_ranking("Vendor") is False
    assert can_user_recalculate_vendor_ranking("Administrator") is True
    assert can_user_recalculate_vendor_ranking("Procurement Manager") is True
    assert can_user_recalculate_vendor_ranking("Vendor") is False


def test_unauthorized_user_cannot_recalculate_rankings():
    with pytest.raises(PermissionError, match="Only Administrator or Procurement Manager"):
        recalculate_vendor_ranking([], "Vendor")


def test_authorized_user_can_recalculate_rankings():
    ranking = recalculate_vendor_ranking(
        [{"vendor_id": 1, "overall_performance_score": 90}],
        "Procurement Manager",
    )
    assert ranking[0]["rank_position"] == 1


def test_performance_write_recalculates_rankings_through_system_helper():
    ranking = recalculate_vendor_ranking_after_performance_write(
        [
            {"vendor_id": 1, "overall_performance_score": 75},
            {"vendor_id": 2, "overall_performance_score": 90},
        ]
    )
    assert [vendor["vendor_id"] for vendor in ranking] == [2, 1]


@pytest.mark.parametrize(
    ("total_deliveries", "on_time_deliveries"),
    [(-1, 0), (2, -1), (2, 3)]
)
def test_on_time_delivery_rate_rejects_impossible_counts(
    total_deliveries,
    on_time_deliveries
):
    with pytest.raises(ValueError):
        calculate_on_time_delivery_rate(total_deliveries, on_time_deliveries)


@pytest.mark.parametrize(
    ("total_orders", "completed_orders"),
    [(-1, 0), (2, -1), (2, 3)]
)
def test_order_completion_rate_rejects_impossible_counts(total_orders, completed_orders):
    with pytest.raises(ValueError):
        calculate_order_completion_rate(total_orders, completed_orders)


def test_overall_performance_rejects_out_of_range_component_score():
    with pytest.raises(ValueError, match="Scores must be between 0 and 100"):
        calculate_overall_performance_score(101, 80, 60, 80)


def test_average_quality_rejects_out_of_range_score():
    with pytest.raises(ValueError, match="Scores must be between 0 and 100"):
        calculate_average_quality_score([80, 101])


def test_average_response_time_rejects_negative_duration():
    with pytest.raises(ValueError, match="Response times cannot be negative"):
        calculate_average_response_time([30, -1])


def test_vendor_ranking_requires_a_valid_overall_score():
    with pytest.raises(ValueError, match="overall performance score"):
        generate_vendor_ranking([{"vendor_id": 1}])


class _PurchaseOrder:
    def __init__(self, purchase_order_id, vendor_id, po_status):
        self.id = purchase_order_id
        self.vendor_id = vendor_id
        self.po_status = po_status


class _Query:
    def __init__(self, value):
        self.value = value

    def filter(self, *_predicates):
        return self

    def first(self):
        return self.value


class _PerformanceDb:
    def __init__(self, purchase_order=None, entry=None):
        self.purchase_order = purchase_order
        self.entry = entry

    def query(self, model):
        value = self.purchase_order if model is PurchaseOrder else self.entry
        return _Query(value)


def test_performance_write_requires_an_existing_purchase_order():
    with pytest.raises(ValueError, match="Purchase order not found"):
        validate_performance_write_eligibility(_PerformanceDb(), 1, 10)


def test_performance_write_rejects_purchase_order_for_another_vendor():
    purchase_order = _PurchaseOrder(10, 2, "Delivered")
    with pytest.raises(ValueError, match="does not belong to the selected vendor"):
        validate_performance_write_eligibility(_PerformanceDb(purchase_order), 1, 10)


@pytest.mark.parametrize("po_status", ["Draft", "Issued", "Cancelled"])
def test_performance_write_requires_delivered_or_completed_purchase_order(po_status):
    purchase_order = _PurchaseOrder(10, 1, po_status)
    with pytest.raises(ValueError, match="Delivered or Completed"):
        validate_performance_write_eligibility(_PerformanceDb(purchase_order), 1, 10)


@pytest.mark.parametrize("po_status", ["Delivered", "Completed"])
def test_performance_write_accepts_delivered_or_completed_purchase_order(po_status):
    purchase_order = _PurchaseOrder(10, 1, po_status)
    assert validate_performance_write_eligibility(
        _PerformanceDb(purchase_order), 1, 10
    ) is purchase_order


def test_duplicate_performance_entry_is_rejected():
    with pytest.raises(ValueError, match="Performance entry already exists"):
        validate_no_duplicate_performance_entry(
            _PerformanceDb(entry=object()), PerformanceRecord, 1, 10
        )


@pytest.mark.parametrize(
    "entry_model",
    [
        type("DeliveryPerformance", (), {
            "vendor_id": PurchaseOrder.vendor_id,
            "purchase_order_id": PurchaseOrder.id,
        }),
        type("ProductQualityEvaluation", (), {
            "vendor_id": PurchaseOrder.vendor_id,
            "purchase_order_id": PurchaseOrder.id,
        }),
        type("CommunicationLog", (), {
            "vendor_id": PurchaseOrder.vendor_id,
            "purchase_order_id": PurchaseOrder.id,
        }),
        type("ServiceRating", (), {
            "vendor_id": PurchaseOrder.vendor_id,
            "purchase_order_id": PurchaseOrder.id,
        }),
    ],
)
def test_duplicate_each_performance_entry_type_is_rejected(entry_model):
    with pytest.raises(ValueError, match="Performance entry already exists"):
        validate_no_duplicate_performance_entry(
            _PerformanceDb(entry=object()), entry_model, 1, 10
        )
