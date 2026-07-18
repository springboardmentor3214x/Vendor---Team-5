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


def _validate_ratings(ratings: list[float]) -> None:
    if any(rating < 1 or rating > 5 for rating in ratings):
        raise ValueError("Ratings must be between 1 and 5")
