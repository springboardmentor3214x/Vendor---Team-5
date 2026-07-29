from unittest.mock import MagicMock, patch
from datetime import datetime
import pytest

from app.services.reliability_service import (
    calculate_reliability_score,
    get_risk_level,
    generate_vendor_recommendation,
    recalculate_vendor_reliability
)
from app.models.vendor import Vendor
from app.models.reliability import VendorReliability, PerformanceTrend, ProcurementRecommendation


def test_reliability_score_calculation():
    score = calculate_reliability_score(
        on_time_delivery_rate=90,
        quality_rating=85,
        response_score=80,
        contract_compliance=95,
        issue_resolution_score=75
    )

    assert score == 86.75


def test_low_risk_level():
    assert get_risk_level(85) == "Low"


def test_medium_risk_level():
    assert get_risk_level(60) == "Medium"


def test_high_risk_level():
    assert get_risk_level(40) == "High"


def test_recommendation_for_good_vendor():
    assert generate_vendor_recommendation(85) == "Recommended vendor for procurement"


def test_recommendation_for_medium_vendor():
    assert generate_vendor_recommendation(60) == "Use with caution and monitor performance"


def test_recommendation_for_poor_vendor():
    assert generate_vendor_recommendation(40) == "High risk vendor, avoid for critical procurement"


@patch("app.services.reliability_service.calculate_communication_score")
def test_recalculate_vendor_reliability(mock_comm_score):
    # Mock communication score converter to return 80
    mock_comm_score.return_value = 80.0

    # Arrange: Create mock DB session and query results
    db = MagicMock()
    
    # Mock Vendor
    mock_vendor = Vendor(
        id=1,
        company_name="Test Vendor",
        email="test@vendor.com",
        reliability_score=0.0
    )
    
    # Mock VendorReliability details row
    mock_rel = VendorReliability(vendor_id=1)
    
    # Mock PerformanceTrend row
    mock_trend = PerformanceTrend(vendor_id=1, year=2026, month=7)
    
    # Mock ProcurementRecommendation row
    mock_rec = ProcurementRecommendation(vendor_id=1)

    # Setup database query mock behavior
    def mock_query(model):
        query_mock = MagicMock()
        
        # When querying model counts or averages
        if hasattr(model, "_from_objects") and len(model._from_objects) > 0:
            label = str(model._from_objects[0])
            # We can handle count/avg scalar return values
            query_mock.filter.return_value.scalar.return_value = 5.0
            return query_mock

        if model == Vendor:
            query_mock.filter.return_value.first.return_value = mock_vendor
        elif model == VendorReliability:
            query_mock.filter.return_value.first.return_value = mock_rel
        elif model == PerformanceTrend:
            query_mock.filter.return_value.first.return_value = mock_trend
        elif model == ProcurementRecommendation:
            query_mock.filter.return_value.first.return_value = mock_rec
        else:
            query_mock.filter.return_value.first.return_value = None
            query_mock.filter.return_value.scalar.return_value = 0
            
        return query_mock

    db.query.side_effect = mock_query

    # Act: Run calculation
    result = recalculate_vendor_reliability(vendor_id=1, db=db)

    # Assert
    assert result is not None
    assert mock_vendor.reliability_score > 0.0
    assert result.reliability_score == mock_vendor.reliability_score
    assert result.risk_level in ["Low", "Medium", "High"]
    db.commit.assert_called()