from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ReportFilterParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start_date: Optional[date] = Field(default=None, alias="startDate")
    end_date: Optional[date] = Field(default=None, alias="endDate")
    vendor_id: Optional[int] = Field(default=None, alias="vendorId")
    category_id: Optional[int] = Field(default=None, alias="categoryId")
    department: Optional[str] = None
    status: Optional[str] = None
    min_reliability_score: Optional[float] = Field(default=None, alias="minReliabilityScore")


class ReportItemSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key: str
    title: str
    description: str
    formats: List[str]  # ["json", "csv", "pdf"]
    status: str = "ready"


class ReportListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: List[ReportItemSummary]
    generated_at: datetime = Field(alias="generatedAt")


# --- Individual Report Row Schemas ---

class VendorPerformanceReportRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vendor_id: int = Field(alias="vendorId")
    vendor_name: str = Field(alias="vendorName")
    category: str
    total_pos_completed: int = Field(alias="totalPosCompleted")
    on_time_delivery_pct: float = Field(alias="onTimeDeliveryPct")
    delayed_deliveries: int = Field(alias="delayedDeliveries")
    product_quality_rating: float = Field(alias="productQualityRating")
    communication_efficiency: float = Field(alias="communicationEfficiency")
    issue_resolution_score: float = Field(alias="issueResolutionScore")
    overall_service_rating: float = Field(alias="overallServiceRating")
    vendor_reliability_score: float = Field(alias="vendorReliabilityScore")
    risk_level: str = Field(alias="riskLevel")


class ProcurementReportRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    metric_name: str = Field(alias="metricName")
    metric_value: Any = Field(alias="metricValue")
    details: Optional[str] = None


class PurchaseOrderReportRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    po_number: str = Field(alias="poNumber")
    vendor_name: str = Field(alias="vendorName")
    category: str
    purchase_date: Optional[str] = Field(default=None, alias="purchaseDate")
    expected_delivery_date: Optional[str] = Field(default=None, alias="expectedDeliveryDate")
    actual_completion_date: Optional[str] = Field(default=None, alias="actualCompletionDate")
    order_value: float = Field(alias="orderValue")
    po_status: str = Field(alias="poStatus")
    invoice_status: str = Field(alias="invoiceStatus")
    department: str


class ComplianceReportRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vendor_id: int = Field(alias="vendorId")
    vendor_name: str = Field(alias="vendorName")
    certification_name: str = Field(alias="certificationName")
    compliance_type: str = Field(alias="complianceType")
    status: str
    verification_date: Optional[str] = Field(default=None, alias="verificationDate")
    expiry_date: Optional[str] = Field(default=None, alias="expiryDate")
    remarks: Optional[str] = None


class ContractReportRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    contract_number: str = Field(alias="contractNumber")
    vendor_name: str = Field(alias="vendorName")
    contract_title: str = Field(alias="contractTitle")
    contract_type: str = Field(alias="contractType")
    contract_value: float = Field(alias="contractValue")
    start_date: Optional[str] = Field(default=None, alias="startDate")
    end_date: Optional[str] = Field(default=None, alias="endDate")
    renewal_status: str = Field(alias="renewalStatus")
    responsible_manager: str = Field(alias="responsibleManager")
    compliance_status: str = Field(alias="complianceStatus")
    days_to_expiry: Optional[int] = Field(default=None, alias="daysToExpiry")


class ExecutiveSummaryReportOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_registered_vendors: int = Field(alias="totalRegisteredVendors")
    active_vendors: int = Field(alias="activeVendors")
    total_procurement_expenditure: float = Field(alias="totalProcurementExpenditure")
    average_reliability_score: float = Field(alias="averageReliabilityScore")
    procurement_completion_rate: float = Field(alias="procurementCompletionRate")
    compliance_percentage: float = Field(alias="compliancePercentage")

    top_performing_vendors: List[str] = Field(alias="topPerformingVendors")
    delayed_deliveries_count: int = Field(alias="delayedDeliveriesCount")
    contracts_near_expiry_count: int = Field(alias="contractsNearExpiryCount")
