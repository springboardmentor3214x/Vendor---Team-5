from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class VendorReliabilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    vendor_id: int = Field(alias="vendorId")
    delivery_score: float = Field(alias="deliveryScore")
    quality_score: float = Field(alias="qualityScore")
    communication_score: float = Field(alias="communicationScore")
    compliance_score: float = Field(alias="complianceScore")
    issue_resolution_score: float = Field(alias="issueResolutionScore")
    reliability_score: float = Field(alias="reliabilityScore")
    risk_level: str = Field(alias="riskLevel")
    recommendation: Optional[str] = None
    updated_at: datetime = Field(alias="updatedAt")

class PerformanceTrendOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    vendor_id: int = Field(alias="vendorId")
    year: int
    month: int
    reliability_score: float = Field(alias="reliabilityScore")
    delivery_score: float = Field(alias="deliveryScore")
    quality_score: float = Field(alias="qualityScore")
    communication_score: float = Field(alias="communicationScore")
    compliance_score: float = Field(alias="complianceScore")
    issue_resolution_score: float = Field(alias="issueResolutionScore")
    created_at: datetime = Field(alias="createdAt")

class ProcurementRecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    vendor_id: int = Field(alias="vendorId")
    vendor_name: Optional[str] = Field(default=None, alias="vendorName")
    vendor_category: Optional[str] = Field(default=None, alias="vendorCategory")
    reliability_score: float = Field(alias="reliabilityScore")
    risk_level: str = Field(alias="riskLevel")
    recommendation_status: str = Field(alias="recommendationStatus")
    reason: Optional[str] = None
    updated_at: datetime = Field(alias="updatedAt")

class VendorRankItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    vendor_id: int = Field(alias="vendorId")
    vendor_name: str = Field(alias="vendorName")
    vendor_category: str = Field(alias="vendorCategory")
    reliability_score: float = Field(alias="reliabilityScore")
    risk_level: str = Field(alias="riskLevel")
    rank_position: int = Field(alias="rankPosition")

class ReliabilityDashboardOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    total_vendors_evaluated: int = Field(alias="totalVendorsEvaluated")
    average_reliability_score: float = Field(alias="averageReliabilityScore")
    high_reliability_count: int = Field(alias="highReliabilityCount")
    medium_reliability_count: int = Field(alias="mediumReliabilityCount")
    high_risk_count: int = Field(alias="highRiskCount")
    top_ranked_vendors: list[VendorRankItem] = Field(alias="topRankedVendors")

class ReliabilityRiskItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    vendor_id: int = Field(alias="vendorId")
    vendor_name: str = Field(alias="vendorName")
    vendor_category: str = Field(alias="vendorCategory")
    reliability_score: float = Field(alias="reliabilityScore")
    risk_level: str = Field(alias="riskLevel")

class ReliabilityRecalculationResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    message: str
    recalculated_vendors: int = Field(alias="recalculatedVendors")
