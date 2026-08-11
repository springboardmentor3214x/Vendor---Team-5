from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ReportFilterParams(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    start_date: date | None = Field(default=None, alias="startDate")
    end_date: date | None = Field(default=None, alias="endDate")
    department: str | None = None
    vendor_id: int | None = Field(default=None, alias="vendorId")
    vendor_name: str | None = Field(default=None, alias="vendorName")
    vendor_category: str | None = Field(default=None, alias="vendorCategory")
    procurement_status: str | None = Field(default=None, alias="procurementStatus")
    purchase_order_status: str | None = Field(default=None, alias="purchaseOrderStatus")
    contract_status: str | None = Field(default=None, alias="contractStatus")
    compliance_status: str | None = Field(default=None, alias="complianceStatus")
    reliability_level: str | None = Field(default=None, alias="reliabilityLevel")


class ReportPreviewOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    report_type: str = Field(alias="reportType")
    rows: list[dict[str, Any]]
    metadata: dict[str, Any]


class ReportChartOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    report_type: str = Field(alias="reportType")
    data: dict[str, Any]
