from pydantic import BaseModel, ConfigDict, Field


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
