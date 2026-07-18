from datetime import date, datetime

from app.services.performance_service import (
    calculate_communication_score,
    calculate_delivery_delay,
    calculate_delivery_score,
    calculate_overall_performance_score,
    calculate_quality_score,
    calculate_response_duration_minutes,
    calculate_service_rating_score,
    get_delivery_status,
    get_performance_status
)


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
