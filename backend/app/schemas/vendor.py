from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


ALLOWED_VENDOR_STATUSES = {"Active", "Pending", "Inactive", "Suspended", "Rejected"}
ALLOWED_APPROVAL_STATUSES = {"Pending", "Approved", "Rejected"}
ALLOWED_DOCUMENT_TYPES = {
    "GST Certificate",
    "PAN Card",
    "Company Registration Certificate",
    "ISO Certificate",
    "Other Supporting Document",
}


class VendorCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    description: Optional[str] = None
    is_active: bool = Field(alias="isActive")


class VendorContactCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    contact_person_name: str = Field(alias="contactPerson", min_length=2, max_length=150)
    designation: Optional[str] = Field(default=None, alias="designation")
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(default=None, alias="phone")
    is_primary: bool = Field(default=False, alias="isPrimary")


class VendorContactOut(VendorContactCreate):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    vendor_id: int = Field(alias="vendorId")


class VendorCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    company_name: str = Field(alias="companyName", min_length=2, max_length=255)
    category_id: Optional[int] = Field(default=None, alias="categoryId")
    vendor_category: Optional[str] = Field(default=None, alias="vendorCategory")
    contact_person_name: str = Field(alias="contactPerson", min_length=2, max_length=150)
    designation: Optional[str] = Field(default=None, alias="designation")
    email: EmailStr
    phone_number: str = Field(alias="phone", min_length=7, max_length=20)
    alternate_phone: Optional[str] = Field(default=None, alias="alternatePhone")
    gst_number: Optional[str] = Field(default=None, alias="gstNumber")
    pan_number: Optional[str] = Field(default=None, alias="panNumber")
    company_registration_number: Optional[str] = Field(default=None, alias="registrationNumber")
    address_line1: Optional[str] = Field(default=None, alias="address1")
    address_line2: Optional[str] = Field(default=None, alias="address2")
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    bank_account_number: Optional[str] = Field(default=None, alias="bankAccountNumber")
    ifsc_code: Optional[str] = Field(default=None, alias="ifscCode")
    payment_terms: Optional[str] = Field(default=None, alias="paymentTerms")
    vendor_status: Optional[str] = Field(default="Pending", alias="vendorStatus")

    @field_validator("vendor_status")
    @classmethod
    def validate_vendor_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if value not in ALLOWED_VENDOR_STATUSES:
            raise ValueError("Invalid vendor status")
        return value


class VendorUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    company_name: Optional[str] = Field(default=None, alias="companyName")
    category_id: Optional[int] = Field(default=None, alias="categoryId")
    vendor_category: Optional[str] = Field(default=None, alias="vendorCategory")
    contact_person_name: Optional[str] = Field(default=None, alias="contactPerson")
    designation: Optional[str] = Field(default=None, alias="designation")
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(default=None, alias="phone")
    alternate_phone: Optional[str] = Field(default=None, alias="alternatePhone")
    gst_number: Optional[str] = Field(default=None, alias="gstNumber")
    pan_number: Optional[str] = Field(default=None, alias="panNumber")
    company_registration_number: Optional[str] = Field(default=None, alias="registrationNumber")
    address_line1: Optional[str] = Field(default=None, alias="address1")
    address_line2: Optional[str] = Field(default=None, alias="address2")
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    bank_account_number: Optional[str] = Field(default=None, alias="bankAccountNumber")
    ifsc_code: Optional[str] = Field(default=None, alias="ifscCode")
    payment_terms: Optional[str] = Field(default=None, alias="paymentTerms")
    vendor_status: Optional[str] = Field(default=None, alias="vendorStatus")

    @field_validator("vendor_status")
    @classmethod
    def validate_vendor_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if value not in ALLOWED_VENDOR_STATUSES:
            raise ValueError("Invalid vendor status")
        return value


class VendorApprovalAction(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    remarks: Optional[str] = None


class VendorDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    vendor_id: int = Field(alias="vendorId")
    document_type: str = Field(alias="documentType")
    file_name: str = Field(alias="fileName")
    message: str

    @field_validator("document_type")
    @classmethod
    def validate_document_type(cls, value: str) -> str:
        if value not in ALLOWED_DOCUMENT_TYPES:
            raise ValueError("Invalid document type")
        return value


class VendorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    company_name: str = Field(alias="companyName")
    category_id: Optional[int] = Field(default=None, alias="categoryId")
    vendor_category: Optional[str] = Field(default=None, alias="vendorCategory")
    contact_person_name: str = Field(alias="contactPerson")
    designation: Optional[str] = None
    email: EmailStr
    phone_number: str = Field(alias="phone")
    alternate_phone: Optional[str] = Field(default=None, alias="alternatePhone")
    gst_number: Optional[str] = Field(default=None, alias="gstNumber")
    pan_number: Optional[str] = Field(default=None, alias="panNumber")
    company_registration_number: Optional[str] = Field(default=None, alias="registrationNumber")
    address_line1: Optional[str] = Field(default=None, alias="address1")
    address_line2: Optional[str] = Field(default=None, alias="address2")
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    bank_account_number: Optional[str] = Field(default=None, alias="bankAccountNumber")
    ifsc_code: Optional[str] = Field(default=None, alias="ifscCode")
    payment_terms: Optional[str] = Field(default=None, alias="paymentTerms")
    vendor_status: str = Field(alias="vendorStatus")
    approval_status: str = Field(alias="approvalStatus")
    reliability_score: Optional[float] = Field(default=0.0, alias="reliabilityScore")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    category: Optional[VendorCategoryOut] = None

    @field_validator("vendor_status")
    @classmethod
    def validate_vendor_status(cls, value: str) -> str:
        if value not in ALLOWED_VENDOR_STATUSES:
            raise ValueError("Invalid vendor status")
        return value

    @field_validator("approval_status")
    @classmethod
    def validate_approval_status(cls, value: str) -> str:
        if value not in ALLOWED_APPROVAL_STATUSES:
            raise ValueError("Invalid approval status")
        return value