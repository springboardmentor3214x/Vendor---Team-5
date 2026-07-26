from datetime import date, datetime
from math import isfinite

from app.models.purchase_order import PurchaseOrder
from app.utils.constants import (
    PURCHASE_ORDER_STATUS_DELIVERED,
    PURCHASE_ORDER_STATUS_COMPLETED,
    ROLE_ADMIN,
    ROLE_PROCUREMENT_MANAGER,
)


PERFORMANCE_WRITEABLE_PO_STATUSES = frozenset({
    PURCHASE_ORDER_STATUS_DELIVERED,
    PURCHASE_ORDER_STATUS_COMPLETED,
})
ON_TIME_DELIVERY_STATUSES = frozenset({"Early Delivery", "On-Time Delivery"})
DELAYED_DELIVERY_STATUS = "Delayed Delivery"


def calculate_delivery_delay(
    expected_delivery_date: date,
    actual_delivery_date: date
) -> int:
    """Return the number of days a delivery was early or late."""
    return (actual_delivery_date - expected_delivery_date).days


def get_delivery_status(
    expected_delivery_date: date,
    actual_delivery_date: date
) -> str:
    """Classify a delivery as early, on time, or delayed."""
    delay_days = calculate_delivery_delay(
        expected_delivery_date,
        actual_delivery_date
    )
    if delay_days < 0:
        return "Early Delivery"
    if delay_days == 0:
        return "On-Time Delivery"
    return "Delayed Delivery"


def calculate_delivery_score(delay_days: int) -> float:
    """Convert delivery timeliness into a score out of 100."""
    _validate_integer(delay_days, "Delay days")
    if delay_days <= 0:
        return 100.0
    if delay_days <= 2:
        return 80.0
    if delay_days <= 5:
        return 60.0
    return 40.0


def calculate_quality_score(
    material_quality: float,
    packaging_quality: float,
    quantity_accuracy: float,
    specification_compliance: float,
    product_defects: int = 0
) -> float:
    """Calculate quality score from 1-to-5 ratings and defect penalties."""
    ratings = [
        material_quality,
        packaging_quality,
        quantity_accuracy,
        specification_compliance
    ]
    _validate_ratings(ratings)
    _validate_non_negative_integer(product_defects, "Product defects")

    return round(max(0, (sum(ratings) / len(ratings)) * 20 - product_defects * 5), 2)


def calculate_response_duration_minutes(
    message_sent_time: datetime,
    vendor_response_time: datetime
) -> float:
    """Return the vendor response duration in minutes."""
    duration_minutes = (vendor_response_time - message_sent_time).total_seconds() / 60
    if duration_minutes < 0:
        raise ValueError("Vendor response time cannot be before message sent time")
    return round(duration_minutes, 2)


def calculate_communication_score(response_duration_minutes: float) -> float:
    """Convert a response duration into a communication score out of 100."""
    _validate_finite_number(response_duration_minutes, "Response duration")
    if response_duration_minutes < 0:
        raise ValueError("Response duration cannot be negative")
    if response_duration_minutes <= 120:
        return 100.0
    if response_duration_minutes <= 360:
        return 80.0
    if response_duration_minutes <= 1440:
        return 60.0
    return 40.0


def calculate_service_rating_score(
    professionalism: float,
    customer_support: float,
    documentation_quality: float,
    flexibility: float,
    communication_effectiveness: float,
    issue_resolution: float
) -> float:
    """Convert six 1-to-5 service ratings into a score out of 100."""
    ratings = [
        professionalism,
        customer_support,
        documentation_quality,
        flexibility,
        communication_effectiveness,
        issue_resolution
    ]
    _validate_ratings(ratings)
    return round((sum(ratings) / len(ratings)) * 20, 2)


def calculate_overall_performance_score(
    delivery_score: float,
    quality_score: float,
    communication_score: float,
    service_rating_score: float
) -> float:
    """Calculate the weighted overall vendor performance score."""
    _validate_scores([
        delivery_score,
        quality_score,
        communication_score,
        service_rating_score
    ])
    return round(
        delivery_score * 0.30
        + quality_score * 0.30
        + communication_score * 0.20
        + service_rating_score * 0.20,
        2
    )


def get_performance_status(overall_score: float) -> str:
    """Classify overall vendor performance."""
    _validate_scores([overall_score])
    if overall_score >= 80:
        return "Excellent"
    if overall_score >= 60:
        return "Good"
    if overall_score >= 40:
        return "Average"
    return "Poor"


def calculate_on_time_delivery_rate(
    total_deliveries: int,
    on_time_deliveries: int
) -> float:
    """Return the percentage of deliveries completed on time."""
    _validate_completed_count(total_deliveries, on_time_deliveries, "On-time deliveries")
    if total_deliveries == 0:
        return 0.0
    return round((on_time_deliveries / total_deliveries) * 100, 2)


def calculate_on_time_delivery_rate_from_statuses(delivery_statuses: list[str]) -> float:
    """Return the on-time percentage for completed delivery status records."""
    on_time_deliveries = sum(
        status in ON_TIME_DELIVERY_STATUSES for status in delivery_statuses
    )
    return calculate_on_time_delivery_rate(len(delivery_statuses), on_time_deliveries)


def calculate_delayed_delivery_count(delivery_statuses: list[str]) -> int:
    """Return the number of delayed deliveries."""
    return delivery_statuses.count(DELAYED_DELIVERY_STATUS)


def calculate_average_score(scores: list[float]) -> float:
    """Return the rounded average for a collection of performance scores."""
    if not scores:
        return 0
    return round(sum(scores) / len(scores), 2)


def calculate_average_delivery_score(delivery_scores: list[float]) -> float:
    """Return the average delivery-timeliness score, distinct from the on-time rate."""
    if not delivery_scores:
        return 0.0
    _validate_scores(delivery_scores)
    return calculate_average_score(delivery_scores)


def calculate_average_quality_score(quality_scores: list[float]) -> float:
    """Return the average quality score."""
    if not quality_scores:
        return 0.0
    _validate_scores(quality_scores)
    return calculate_average_score(quality_scores)


def calculate_average_communication_score(communication_scores: list[float]) -> float:
    """Return the average communication score."""
    if not communication_scores:
        return 0.0
    _validate_scores(communication_scores)
    return calculate_average_score(communication_scores)


def calculate_average_service_rating_score(service_rating_scores: list[float]) -> float:
    """Return the average service-rating score."""
    if not service_rating_scores:
        return 0.0
    _validate_scores(service_rating_scores)
    return calculate_average_score(service_rating_scores)


def calculate_average_response_time(response_times: list[float]) -> float:
    """Return the average vendor response time."""
    if not response_times:
        return 0.0
    for response_time in response_times:
        _validate_finite_number(response_time, "Response time")
        if response_time < 0:
            raise ValueError("Response times cannot be negative")
    return round(sum(response_times) / len(response_times), 2)


def calculate_order_completion_rate(
    total_orders: int,
    completed_orders: int
) -> float:
    """Return the percentage of orders completed."""
    _validate_completed_count(total_orders, completed_orders, "Completed orders")
    if total_orders == 0:
        return 0.0
    return round((completed_orders / total_orders) * 100, 2)


def generate_vendor_ranking(vendor_scores: list[dict]) -> list[dict]:
    """Rank vendors by overall performance score in descending order."""
    for vendor in vendor_scores:
        if not isinstance(vendor, dict):
            raise ValueError("Each vendor score must be a dictionary")
        if "overall_performance_score" not in vendor:
            raise ValueError("Each vendor must include an overall performance score")
        _validate_scores([vendor["overall_performance_score"]])
    sorted_vendors = sorted(
        vendor_scores,
        key=lambda vendor: vendor["overall_performance_score"],
        reverse=True
    )
    return [
        {**vendor, "rank_position": position}
        for position, vendor in enumerate(sorted_vendors, start=1)
    ]


def can_user_recalculate_vendor_ranking(user_role: str) -> bool:
    """Return whether the role is permitted to recalculate vendor rankings."""
    return user_role in {ROLE_ADMIN, ROLE_PROCUREMENT_MANAGER}


def can_recalculate_vendor_ranking(user_role: str) -> bool:
    """Return whether the role may recalculate vendor rankings."""
    return can_user_recalculate_vendor_ranking(user_role)


def recalculate_vendor_ranking_after_performance_write(
    vendor_scores: list[dict],
) -> list[dict]:
    """Recalculate rankings after a successful system performance write."""
    return generate_vendor_ranking(vendor_scores)


def recalculate_vendor_ranking(
    vendor_scores: list[dict],
    user_role: str,
) -> list[dict]:
    """Manually recalculate rankings only for authorized procurement roles."""
    if not can_user_recalculate_vendor_ranking(user_role):
        raise PermissionError(
            "Only Administrator or Procurement Manager can recalculate vendor rankings"
        )
    return generate_vendor_ranking(vendor_scores)


def validate_performance_write_eligibility(
    db,
    vendor_id: int,
    purchase_order_id: int,
) -> PurchaseOrder:
    """Return an eligible PO or raise a business-rule error for a performance write."""
    purchase_order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == purchase_order_id
    ).first()
    if not purchase_order:
        raise ValueError("Purchase order not found")
    if purchase_order.vendor_id != vendor_id:
        raise ValueError("Purchase order does not belong to the selected vendor")
    if purchase_order.po_status not in PERFORMANCE_WRITEABLE_PO_STATUSES:
        raise ValueError(
            "Performance entries can be recorded only for Delivered or Completed purchase orders"
        )
    return purchase_order


def validate_no_duplicate_performance_entry(
    db,
    entry_model,
    vendor_id: int,
    purchase_order_id: int,
) -> None:
    """Reject a second entry of the same performance type for a vendor and PO."""
    existing_entry = db.query(entry_model).filter(
        entry_model.vendor_id == vendor_id,
        entry_model.purchase_order_id == purchase_order_id,
    ).first()
    if existing_entry:
        raise ValueError(
            "Performance entry already exists for this vendor and purchase order"
        )


def _validate_ratings(ratings: list[float]) -> None:
    for rating in ratings:
        _validate_finite_number(rating, "Rating")
        if rating < 1 or rating > 5:
            raise ValueError("Ratings must be between 1 and 5")


def _validate_scores(scores: list[float]) -> None:
    for score in scores:
        _validate_finite_number(score, "Score")
        if score < 0 or score > 100:
            raise ValueError("Scores must be between 0 and 100")


def _validate_completed_count(total: int, completed: int, completed_label: str) -> None:
    _validate_non_negative_integer(total, "Total count")
    _validate_non_negative_integer(completed, completed_label)
    if completed > total:
        raise ValueError(f"{completed_label} cannot exceed total count")


def _validate_non_negative_integer(value: int, label: str) -> None:
    _validate_integer(value, label)
    if value < 0:
        raise ValueError(f"{label} cannot be negative")


def _validate_integer(value: int, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")


def _validate_finite_number(value: float, label: str) -> None:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a finite number")
    try:
        valid = isfinite(value)
    except TypeError as error:
        raise ValueError(f"{label} must be a finite number") from error
    if not valid:
        raise ValueError(f"{label} must be a finite number")
