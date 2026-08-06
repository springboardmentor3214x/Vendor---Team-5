from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class VendorReliabilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vendor_id: int
    delivery_score: float
    quality_score: float
    communication_score: float
    compliance_score: float
    issue_resolution_score: float
    procurement_history_score: float = 0.0
    reliability_score: float
    risk_level: str
    recommendation: Optional[str] = None
    updated_at: datetime


class PerformanceTrendOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vendor_id: int
    year: int
    month: int
    reliability_score: float
    delivery_score: float
    quality_score: float
    communication_score: float
    compliance_score: float
    issue_resolution_score: float
    procurement_history_score: float = 0.0
    created_at: datetime


class ProcurementRecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vendor_id: int
    vendor_name: Optional[str] = None
    vendor_category: Optional[str] = None
    reliability_score: float
    risk_level: str
    recommendation_status: str
    reason: Optional[str] = None
    updated_at: datetime


class VendorRankItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    vendor_id: int
    vendor_name: str
    vendor_category: str
    reliability_score: float
    risk_level: str
    rank_position: int


class ReliabilityDashboardOut(BaseModel):
    total_vendors_evaluated: int
    average_reliability_score: float
    high_reliability_count: int
    medium_reliability_count: int
    high_risk_count: int
    top_ranked_vendors: List[VendorRankItem]
