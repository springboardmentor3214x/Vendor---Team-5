from datetime import datetime
from pydantic import BaseModel


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
    product_defects: int


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
    vendor_id: int
    purchase_order_id: int
    overall_score: float
    performance_status: str
    notes: str | None = None
    evaluation_date: datetime


class PerformanceDashboardOut(BaseModel):
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


class PerformanceRecordOut(BaseModel):
    id: int
    vendor_id: int
    total_completed_orders: int
    on_time_delivery_rate: float
    delayed_delivery_count: int
    average_quality_score: float
    average_response_time: float
    average_service_rating_score: float
    overall_performance_score: float
    performance_status: str
    evaluation_date: datetime
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RankingItem(BaseModel):
    vendor_id: int
    vendor_name: str | None = None
    overall_score: float
    rank: int


class VendorRankingOut(BaseModel):
    rankings: list[RankingItem]