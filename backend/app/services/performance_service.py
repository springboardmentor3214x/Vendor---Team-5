from datetime import date, datetime


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
    if product_defects < 0:
        raise ValueError("Product defects cannot be negative")

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
    return round(
        delivery_score * 0.30
        + quality_score * 0.30
        + communication_score * 0.20
        + service_rating_score * 0.20,
        2
    )


def get_performance_status(overall_score: float) -> str:
    """Classify overall vendor performance."""
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
    if total_deliveries == 0:
        return 0.0
    return round((on_time_deliveries / total_deliveries) * 100, 2)


def calculate_delayed_delivery_count(delivery_statuses: list[str]) -> int:
    """Return the number of delayed deliveries."""
    return delivery_statuses.count("Delayed Delivery")


def calculate_average_quality_score(quality_scores: list[float]) -> float:
    """Return the average quality score."""
    if not quality_scores:
        return 0.0
    return round(sum(quality_scores) / len(quality_scores), 2)


def calculate_average_response_time(response_times: list[float]) -> float:
    """Return the average vendor response time."""
    if not response_times:
        return 0.0
    return round(sum(response_times) / len(response_times), 2)


def calculate_order_completion_rate(
    total_orders: int,
    completed_orders: int
) -> float:
    """Return the percentage of orders completed."""
    if total_orders == 0:
        return 0.0
    return round((completed_orders / total_orders) * 100, 2)


def generate_vendor_ranking(vendor_scores: list[dict]) -> list[dict]:
    """Rank vendors by overall performance score in descending order."""
    sorted_vendors = sorted(
        vendor_scores,
        key=lambda vendor: vendor["overall_performance_score"],
        reverse=True
    )
    return [
        {**vendor, "rank_position": position}
        for position, vendor in enumerate(sorted_vendors, start=1)
    ]


def _validate_ratings(ratings: list[float]) -> None:
    if any(rating < 1 or rating > 5 for rating in ratings):
        raise ValueError("Ratings must be between 1 and 5")
