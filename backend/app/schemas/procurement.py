from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}
VALID_APPROVAL_STATUSES = {"Pending", "Approved", "Rejected", "Sent Back", "Cancelled"}
VALID_PO_STATUSES = {"Draft", "Issued", "Delivered", "Cancelled", "Completed"}
VALID_DELIVERY_STATUSES = {"Awaiting Shipment", "In Transit", "Delivered", "Delayed", "Completed"}
VALID_PAYMENT_STATUSES = {"Pending", "Verified", "Approved", "Paid", "Rejected"}


# ---------------- Procurement Requests ----------------

class ProcurementRequestCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    title: str = Field(alias="requestTitle", min_length=3, max_length=255)
    department: str = Field(alias="departmentName")
    item_description: str = Field(alias="itemDescription", min_length=3, max_length=500)
    product_name: str = Field(alias="itemProductName", min_length=2, max_length=255)
    product_category: str = Field(alias="productCategory")
    quantity: int = Field(default=1, alias="quantityRequired", gt=0)
    unit_of_measurement: Optional[str] = Field(default=None, alias="unitOfMeasurement")
    estimated_budget: float = Field(default=0.0, alias="estimatedBudget", ge=0)
    required_delivery_date: date = Field(alias="requiredDeliveryDate")
    priority: str = Field(default="Medium", alias="priority")
    business_justification: str = Field(alias="businessJustification", min_length=3, max_length=1000)
    additional_remarks: Optional[str] = Field(default=None, alias="additionalRemarks")
    requested_by: Optional[int] = Field(default=None, alias="requestedBy")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str) -> str:
        if value not in VALID_PRIORITIES:
            raise ValueError("Invalid priority")
        return value


class ProcurementRequestUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    title: Optional[str] = Field(default=None, alias="requestTitle")
    department: Optional[str] = Field(default=None, alias="departmentName")
    item_description: Optional[str] = Field(default=None, alias="itemDescription")
    product_name: Optional[str] = Field(default=None, alias="itemProductName")
    product_category: Optional[str] = Field(default=None, alias="productCategory")
    quantity: Optional[int] = Field(default=None, alias="quantityRequired", gt=0)
    unit_of_measurement: Optional[str] = Field(default=None, alias="unitOfMeasurement")
    estimated_budget: Optional[float] = Field(default=None, alias="estimatedBudget", ge=0)
    required_delivery_date: Optional[date] = Field(default=None, alias="requiredDeliveryDate")
    priority: Optional[str] = Field(default=None, alias="priority")
    business_justification: Optional[str] = Field(default=None, alias="businessJustification")
    additional_remarks: Optional[str] = Field(default=None, alias="additionalRemarks")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if value not in VALID_PRIORITIES:
            raise ValueError("Invalid priority")
        return value


class ProcurementRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    request_number: str = Field(alias="requestNumber")
    title: str = Field(alias="requestTitle")
    department: str = Field(alias="departmentName")
    item_description: str = Field(alias="itemDescription")
    product_name: str = Field(alias="itemProductName")
    product_category: str = Field(alias="productCategory")
    quantity: int = Field(alias="quantityRequired")
    unit_of_measurement: Optional[str] = Field(default=None, alias="unitOfMeasurement")
    estimated_budget: float = Field(alias="estimatedBudget")
    required_delivery_date: datetime = Field(alias="requiredDeliveryDate")
    priority: str
    business_justification: str = Field(alias="businessJustification")
    additional_remarks: Optional[str] = Field(default=None, alias="additionalRemarks")
    requested_by: Optional[int] = Field(default=None, alias="requestedBy")
    request_date: datetime = Field(alias="requestDate")
    approval_status: str = Field(alias="approvalStatus")
    approval_remarks: Optional[str] = Field(default=None, alias="approvalRemarks")
    approved_by: Optional[int] = Field(default=None, alias="approvedBy")
    approved_date: Optional[datetime] = Field(default=None, alias="approvedDate")
    vendor_id: Optional[int] = Field(default=None, alias="vendorId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class ProcurementApprovalAction(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    approved_by: Optional[int] = Field(default=None, alias="approvedBy")
    remarks: Optional[str] = None


class VendorAssignmentAction(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    vendor_id: int = Field(alias="vendorId")


class ApprovedVendorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    company_name: str = Field(alias="companyName")
    contact_person_name: str = Field(alias="contactPerson")
    reliability_score: float = Field(alias="reliabilityScore")
    vendor_status: str = Field(alias="vendorStatus")
    approval_status: str = Field(alias="approvalStatus")


class ProcurementStatusHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    procurement_request_id: int = Field(alias="procurementRequestId")
    old_status: Optional[str] = Field(default=None, alias="oldStatus")
    new_status: str = Field(alias="newStatus")
    changed_by: Optional[int] = Field(default=None, alias="changedBy")
    remarks: Optional[str] = None
    changed_at: datetime = Field(alias="changedAt")


# ---------------- Purchase Orders ----------------

class PurchaseOrderCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    procurement_request_id: int = Field(alias="procurementRequestId")
    contract_id: Optional[int] = Field(default=None, alias="contractId")
    quantity: int = Field(default=1, alias="quantityOrdered", gt=0)
    unit_price: float = Field(default=0.0, alias="unitPrice", ge=0)
    tax_details: Optional[float] = Field(default=0.0, alias="taxDetails")
    shipping_address: Optional[str] = Field(default=None, alias="shippingAddress")
    expected_delivery_date: datetime = Field(alias="expectedDeliveryDate")
    payment_terms: Optional[str] = Field(default=None, alias="paymentTerms")
    created_by: Optional[int] = Field(default=None, alias="createdBy")


class PurchaseOrderStatusUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    po_status: str = Field(alias="poStatus")
    approved_by: Optional[int] = Field(default=None, alias="approvedBy")

    @field_validator("po_status")
    @classmethod
    def validate_po_status(cls, value: str) -> str:
        if value not in VALID_PO_STATUSES:
            raise ValueError("Invalid purchase order status")
        return value


class PurchaseOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    po_number: str = Field(alias="poNumber")
    procurement_request_id: int = Field(alias="procurementRequestId")
    vendor_id: int = Field(alias="vendorId")
    contract_id: Optional[int] = Field(default=None, alias="contractId")
    quantity: int = Field(alias="quantityOrdered")
    unit_price: float = Field(alias="unitPrice")
    total_cost: float = Field(alias="totalCost")
    tax_details: Optional[float] = Field(default=0.0, alias="taxDetails")
    shipping_address: Optional[str] = Field(default=None, alias="shippingAddress")
    expected_delivery_date: datetime = Field(alias="expectedDeliveryDate")
    actual_delivery_date: Optional[datetime] = Field(default=None, alias="actualDeliveryDate")
    payment_terms: Optional[str] = Field(default=None, alias="paymentTerms")
    po_status: str = Field(alias="poStatus")
    created_by: Optional[int] = Field(default=None, alias="createdBy")
    approved_by: Optional[int] = Field(default=None, alias="approvedBy")
    po_date: datetime = Field(alias="poDate")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


# ---------------- Order Tracking ----------------

class OrderTrackingUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    dispatch_date: Optional[datetime] = Field(default=None, alias="dispatchDate")
    actual_delivery_date: Optional[datetime] = Field(default=None, alias="actualDeliveryDate")
    delivery_status: Optional[str] = Field(default=None, alias="deliveryStatus")
    remarks: Optional[str] = None

    @field_validator("delivery_status")
    @classmethod
    def validate_delivery_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if value not in VALID_DELIVERY_STATUSES:
            raise ValueError("Invalid delivery status")
        return value


class OrderTrackingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    purchase_order_id: int = Field(alias="purchaseOrderId")
    dispatch_date: Optional[datetime] = Field(default=None, alias="dispatchDate")
    expected_delivery_date: datetime = Field(alias="expectedDeliveryDate")
    actual_delivery_date: Optional[datetime] = Field(default=None, alias="actualDeliveryDate")
    delivery_status: str = Field(alias="deliveryStatus")
    delay_days: int = Field(default=0, alias="delayDays")
    remarks: Optional[str] = None


# ---------------- Invoices ----------------

class InvoiceCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    purchase_order_id: int = Field(alias="purchaseOrderId")
    invoice_number: str = Field(alias="invoiceNumber")
    invoice_amount: float = Field(alias="invoiceAmount", ge=0)
    tax_amount: Optional[float] = Field(default=0.0, alias="taxAmount", ge=0)
    supporting_document_url: Optional[str] = Field(default=None, alias="supportingInvoiceDocument")
    invoice_date: datetime = Field(alias="invoiceDate")
    due_date: Optional[datetime] = Field(default=None, alias="dueDate")


class InvoiceVerifyAction(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    remarks: Optional[str] = None


class PaymentStatusUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    payment_status: str = Field(alias="paymentStatus")

    @field_validator("payment_status")
    @classmethod
    def validate_payment_status(cls, value: str) -> str:
        if value not in VALID_PAYMENT_STATUSES:
            raise ValueError("Invalid payment status")
        return value


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    invoice_number: str = Field(alias="invoiceNumber")
    purchase_order_id: int = Field(alias="purchaseOrderId")
    invoice_amount: float = Field(alias="invoiceAmount")
    tax_amount: float = Field(alias="taxAmount")
    total_amount: float = Field(alias="totalAmount")
    supporting_document_url: Optional[str] = Field(default=None, alias="supportingInvoiceDocument")
    invoice_date: datetime = Field(alias="invoiceDate")
    due_date: Optional[datetime] = Field(default=None, alias="dueDate")
    paid_date: Optional[datetime] = Field(default=None, alias="paidDate")
    payment_status: str = Field(alias="paymentStatus")
