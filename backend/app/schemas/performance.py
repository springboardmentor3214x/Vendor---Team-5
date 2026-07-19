from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class DeliveryPerformanceCreate(BaseModel):
    vendor_id: int
    purchase_order_id: int
    expected_delivery_date: datetime
    actual_delivery_date: datetime


class QualityPerformanceCreate(BaseModel):
    vendor_id: int
    purchase_order_id: int
    material_quality: float
    packaging_quality: float
    quantity_accuracy: float
    specification_compliance: float
    product_defects: Optional[int] = 0


class CommunicationPerformanceCreate(BaseModel):
    vendor_id: int
    purchase_order_id: int
    message_sent_time: datetime
    vendor_response_time: datetime


class ServiceRatingCreate(BaseModel):
    vendor_id: int
    purchase_order_id: int
    professionalism: float
    customer_support: float
    documentation_quality: float
    flexibility: float
    communication_effectiveness: float
    issue_resolution: float


class PerformanceActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    vendor_id: int
    purchase_order_id: int
    overall_score: float
    performance_status: str
    notes: Optional[str] = None
    evaluation_date: datetime


class PerformanceRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vendor_id: int
    procurement_order_id: Optional[int] = None
    on_time_delivery: Optional[float] = None
    quality_rating: Optional[float] = None
    communication_score: Optional[float] = None
    service_rating_score: Optional[float] = None
    overall_score: float
    risk_level: str
    evaluation_date: datetime
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PerformanceDashboardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    total_vendors: int
    average_overall_score: float
    excellent_count: int
    good_count: int
    average_count: int
    poor_count: int
    average_delivery_score: float
    average_quality_score: float
    average_communication_score: float
    average_service_rating_score: float
    completion_rate: float


class VendorRankingItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    vendor_id: int
    vendor_name: Optional[str] = None
    overall_score: float
    rank: int


class VendorRankingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rankings: List[VendorRankingItem]
