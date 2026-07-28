from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


RATING_MIN = 0.0
RATING_MAX = 5.0
VALID_DELIVERY_STATUSES = {"Early Delivery", "On-Time Delivery", "Delayed Delivery"}
VALID_COMMUNICATION_STATUSES = {"Pending", "Responded", "No Response", "Escalated"}


class DeliveryPerformanceCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    vendor_id: int = Field(alias="vendorId")
    purchase_order_id: int = Field(alias="purchaseOrderId")
    expected_delivery_date: datetime = Field(alias="expectedDeliveryDate")
    actual_delivery_date: datetime = Field(alias="actualDeliveryDate")
    remarks: Optional[str] = None


class DeliveryPerformanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    vendor_id: int = Field(alias="vendorId")
    purchase_order_id: int = Field(alias="purchaseOrderId")
    expected_delivery_date: datetime = Field(alias="expectedDeliveryDate")
    actual_delivery_date: datetime = Field(alias="actualDeliveryDate")
    delay_days: int = Field(alias="delayDays")
    delivery_status: str = Field(alias="deliveryStatus")
    remarks: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    @field_validator("delivery_status")
    @classmethod
    def validate_delivery_status(cls, value: str) -> str:
        if value not in VALID_DELIVERY_STATUSES:
            raise ValueError("Invalid delivery status")
        return value


class QualityPerformanceCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    vendor_id: int = Field(alias="vendorId")
    purchase_order_id: int = Field(alias="purchaseOrderId")
    inspection_date: Optional[datetime] = Field(default=None, alias="inspectionDate")
    material_quality: float = Field(alias="materialQuality")
    packaging_quality: float = Field(alias="packagingQuality")
    quantity_accuracy: float = Field(alias="quantityAccuracy")
    specification_compliance: float = Field(alias="specificationCompliance")
    product_defects: int = Field(alias="productDefects", ge=0)
    inspector_remarks: Optional[str] = Field(default=None, alias="inspectorRemarks")

    @field_validator(
        "material_quality",
        "packaging_quality",
        "quantity_accuracy",
        "specification_compliance",
    )
    @classmethod
    def validate_score(cls, value: float) -> float:
        if not (RATING_MIN <= value <= RATING_MAX):
            raise ValueError("Rating values must be between 0 and 5")
        return value


class QualityPerformanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    vendor_id: int = Field(alias="vendorId")
    purchase_order_id: int = Field(alias="purchaseOrderId")
    inspection_date: datetime = Field(alias="inspectionDate")
    material_quality: float = Field(alias="materialQuality")
    packaging_quality: float = Field(alias="packagingQuality")
    quantity_accuracy: float = Field(alias="quantityAccuracy")
    specification_compliance: float = Field(alias="specificationCompliance")
    product_defects: int = Field(alias="productDefects")
    overall_quality_rating: float = Field(alias="overallQualityRating")
    inspector_remarks: Optional[str] = Field(default=None, alias="inspectorRemarks")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class CommunicationPerformanceCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    vendor_id: int = Field(alias="vendorId")
    purchase_order_id: int = Field(alias="purchaseOrderId")
    message_sent_time: datetime = Field(alias="messageSentTime")
    vendor_response_time: datetime = Field(alias="vendorResponseTime")
    remarks: Optional[str] = None


class CommunicationPerformanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    vendor_id: int = Field(alias="vendorId")
    purchase_order_id: int = Field(alias="purchaseOrderId")
    message_sent_time: datetime = Field(alias="messageSentTime")
    vendor_response_time: datetime = Field(alias="vendorResponseTime")
    response_duration_minutes: int = Field(alias="responseDurationMinutes")
    communication_status: str = Field(alias="communicationStatus")
    remarks: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    @field_validator("communication_status")
    @classmethod
    def validate_communication_status(cls, value: str) -> str:
        if value not in VALID_COMMUNICATION_STATUSES:
            raise ValueError("Invalid communication status")
        return value


class ServiceRatingCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    vendor_id: int = Field(alias="vendorId")
    purchase_order_id: int = Field(alias="purchaseOrderId")
    professionalism: float
    customer_support: float = Field(alias="customerSupport")
    documentation_quality: float = Field(alias="documentationQuality")
    flexibility: float
    communication_effectiveness: float = Field(alias="communicationEffectiveness")
    issue_resolution: float = Field(alias="issueResolution")
    comments: Optional[str] = None

    @field_validator(
        "professionalism",
        "customer_support",
        "documentation_quality",
        "flexibility",
        "communication_effectiveness",
        "issue_resolution",
    )
    @classmethod
    def validate_score(cls, value: float) -> float:
        if not (RATING_MIN <= value <= RATING_MAX):
            raise ValueError("Rating values must be between 0 and 5")
        return value


class ServiceRatingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    vendor_id: int = Field(alias="vendorId")
    purchase_order_id: int = Field(alias="purchaseOrderId")
    professionalism: float
    customer_support: float = Field(alias="customerSupport")
    documentation_quality: float = Field(alias="documentationQuality")
    flexibility: float
    communication_effectiveness: float = Field(alias="communicationEffectiveness")
    issue_resolution: float = Field(alias="issueResolution")
    overall_service_rating: float = Field(alias="overallServiceRating")
    comments: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class PerformanceActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    vendor_id: int = Field(alias="vendorId")
    purchase_order_id: int = Field(alias="purchaseOrderId")
    overall_score: float = Field(alias="overallScore")
    performance_status: str = Field(alias="performanceStatus")
    notes: Optional[str] = None
    evaluation_date: datetime = Field(alias="evaluationDate")


class PerformanceDashboardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    total_vendors: int = Field(alias="totalVendors")
    average_overall_score: float = Field(alias="averageOverallScore")
    excellent_count: int = Field(alias="excellentCount")
    good_count: int = Field(alias="goodCount")
    average_count: int = Field(alias="averageCount")
    poor_count: int = Field(alias="poorCount")
    total_completed_orders: int = Field(alias="totalCompletedOrders")
    total_delayed_deliveries: int = Field(alias="totalDelayedDeliveries")
    average_delivery_score: float = Field(alias="averageDeliveryScore")
    average_quality_score: float = Field(alias="averageQualityScore")
    average_communication_score: float = Field(alias="averageCommunicationScore")
    average_service_rating_score: float = Field(alias="averageServiceRatingScore")
    completion_rate: float = Field(alias="completionRate")


class PerformanceRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    vendor_id: int = Field(alias="vendorId")
    total_completed_orders: int = Field(alias="totalCompletedOrders")
    on_time_delivery_rate: float = Field(alias="onTimeDeliveryRate")
    delayed_delivery_count: int = Field(alias="delayedDeliveryCount")
    average_quality_score: float = Field(alias="averageQualityScore")
    average_response_time: float = Field(alias="averageResponseTime")
    average_service_rating_score: float = Field(alias="averageServiceRatingScore")
    overall_performance_score: float = Field(alias="overallPerformanceScore")
    performance_status: str = Field(alias="performanceStatus")
    evaluation_date: datetime = Field(alias="evaluationDate")
    notes: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class RankingItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    vendor_id: int = Field(alias="vendorId")
    vendor_name: Optional[str] = Field(default=None, alias="vendorName")
    delivery_score: float = Field(alias="deliveryScore")
    quality_score: float = Field(alias="qualityScore")
    communication_score: float = Field(alias="communicationScore")
    service_rating_score: float = Field(alias="serviceRatingScore")
    overall_performance_score: float = Field(alias="overallPerformanceScore")
    rank_position: int = Field(alias="rankPosition")


class VendorRankingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    rankings: list[RankingItem]