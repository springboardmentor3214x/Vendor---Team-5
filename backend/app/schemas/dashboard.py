from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import date


class ContractDashboardSummaryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_contracts: int = Field(alias="totalContracts")
    active_contracts: int = Field(alias="activeContracts")
    expired_contracts: int = Field(alias="expiredContracts")
    expiring_soon_contracts: int = Field(alias="expiringSoonContracts")


class ComplianceDashboardSummaryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_compliance_records: int = Field(alias="totalComplianceRecords")
    compliant_count: int = Field(alias="compliantCount")
    non_compliant_count: int = Field(alias="nonCompliantCount")
    pending_count: int = Field(alias="pendingCount")
    expired_count: int = Field(alias="expiredCount")


class DocumentDashboardSummaryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_documents: int = Field(alias="totalDocuments")
    total_certifications: int = Field(alias="totalCertifications")
    expired_certifications: int = Field(alias="expiredCertifications")
    expiring_soon_certifications: int = Field(alias="expiringSoonCertifications")


class NotificationDashboardSummaryOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_notifications: int = Field(alias="totalNotifications")
    unread_notifications: int = Field(alias="unreadNotifications")


class Module6DashboardOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    contracts: ContractDashboardSummaryOut
    compliance: ComplianceDashboardSummaryOut
    documents: DocumentDashboardSummaryOut
    notifications: NotificationDashboardSummaryOut


# --- Module 8 Analytics Schemas ---
class DashboardFilterParams(BaseModel):
    """Optional read-only dashboard filters supported by aggregation helpers."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    vendor_id: int | None = Field(default=None, alias="vendorId")
    department: str | None = None
    project: str | None = Field(default=None, alias="project")
    start_date: date | None = Field(default=None, alias="startDate")
    end_date: date | None = Field(default=None, alias="endDate")


class DashboardDataOut(BaseModel):
    """Wrapper for service-backed analytics whose fields vary by dashboard view."""

class ProcurementStatusSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_requests: int = Field(alias="totalRequests")
    pending_approvals: int = Field(alias="pendingApprovals")
    approved_requests: int = Field(alias="approvedRequests")
    rejected_requests: int = Field(alias="rejectedRequests")

    active_purchase_orders: int = Field(alias="activePurchaseOrders")
    completed_orders: int = Field(alias="completedOrders")
    cancelled_orders: int = Field(alias="cancelledOrders")

    total_procurement_cost: float = Field(alias="totalProcurementCost")
    today_requests: int = Field(alias="todayRequests")
    weekly_completed_orders: int = Field(alias="weeklyCompletedOrders")
    monthly_spending: float = Field(alias="monthlySpending")


class DeliveryStatusSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    on_time_deliveries: int = Field(alias="onTimeDeliveries")
    delayed_deliveries: int = Field(alias="delayedDeliveries")
    delivered_orders: int = Field(alias="deliveredOrders")
    pending_shipments: int = Field(alias="pendingShipments")
    completed_deliveries: int = Field(alias="completedDeliveries")


class VendorPerformanceSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vendor_id: int = Field(alias="vendorId")
    vendor_name: str = Field(alias="vendorName")
    overall_performance_rating: float = Field(alias="overallPerformanceRating")
    delivery_accuracy: float = Field(alias="deliveryAccuracy")
    product_quality_score: float = Field(alias="productQualityScore")
    communication_efficiency: float = Field(alias="communicationEfficiency")
    service_rating: float = Field(alias="serviceRating")
    reliability_score: float = Field(alias="reliabilityScore")
    risk_level: str = Field(alias="riskLevel")


class ProcurementDashboardOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    procurement_summary: ProcurementStatusSummary = Field(alias="procurementSummary")
    delivery_summary: DeliveryStatusSummary = Field(alias="deliverySummary")
    requests_by_department: Dict[str, int] = Field(alias="requestsByDepartment")
    top_vendors: List[VendorPerformanceSummary] = Field(alias="topVendors")


class PersonalizedVendorDashboardOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    vendor_id: int = Field(alias="vendorId")
    company_name: str = Field(alias="companyName")
    reliability_score: float = Field(alias="reliabilityScore")
    overall_performance_score: float = Field(alias="overallPerformanceScore")
    delivery_accuracy: float = Field(alias="deliveryAccuracy")
    product_quality_rating: float = Field(alias="productQualityRating")
    communication_efficiency: float = Field(alias="communicationEfficiency")

    active_purchase_orders: int = Field(alias="activePurchaseOrders")
    completed_orders: int = Field(alias="completedOrders")
    pending_deliveries: int = Field(alias="pendingDeliveries")

    active_contracts: int = Field(alias="activeContracts")
    expiring_contracts: int = Field(alias="expiringContracts")
    unread_messages: int = Field(alias="unreadMessages")
    unread_notifications: int = Field(alias="unreadNotifications")


class AdminDashboardOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_users: int = Field(alias="totalUsers")
    active_users: int = Field(alias="activeUsers")
    total_vendors: int = Field(alias="totalVendors")
    approved_vendors: int = Field(alias="approvedVendors")
    pending_vendors: int = Field(alias="pendingVendors")

    total_procurement_requests: int = Field(alias="totalProcurementRequests")
    total_purchase_orders: int = Field(alias="totalPurchaseOrders")
    total_contract_value: float = Field(alias="totalContractValue")

    compliant_vendors_count: int = Field(alias="compliantVendorsCount")
    total_activity_logs: int = Field(alias="totalActivityLogs")
    total_communication_files: int = Field(alias="totalCommunicationFiles")


class CostAnalysisOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    spending_by_department: Dict[str, float] = Field(alias="spendingByDepartment")
    spending_by_category: Dict[str, float] = Field(alias="spendingByCategory")
    monthly_spending_trend: Dict[str, float] = Field(alias="monthlySpendingTrend")
    total_expenses: float = Field(alias="totalExpenses")


class ChartDataSeries(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chart_type: str = Field(alias="chartType")  # bar, line, pie, doughnut
    title: str
    labels: List[str]
    datasets: List[Dict[str, Any]]


class ChartDataResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    monthly_expenses_chart: ChartDataSeries = Field(alias="monthlyExpensesChart")
    vendor_performance_trend_chart: ChartDataSeries = Field(alias="vendorPerformanceTrendChart")
    category_distribution_chart: ChartDataSeries = Field(alias="categoryDistributionChart")
    contract_status_chart: ChartDataSeries = Field(alias="contractStatusChart")
