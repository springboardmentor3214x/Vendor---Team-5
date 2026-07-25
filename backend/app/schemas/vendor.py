from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class VendorPayload(BaseModel):
    """Fields accepted from the vendor form (snake_case and camelCase)."""

    model_config = ConfigDict(populate_by_name=True)

    company_name: str = Field(alias="companyName")
    category_id: int | None = Field(default=None, alias="categoryId")
    # This is an input-only convenience field; Vendor stores category_id.
    vendor_category: str | None = Field(default=None, alias="vendorCategory")
    contact_person_name: str = Field(alias="contactPersonName")
    designation: str | None = None
    email: EmailStr
    phone_number: str = Field(alias="phoneNumber")
    alternate_phone: str | None = Field(default=None, alias="alternatePhone")
    gst_number: str | None = Field(default=None, alias="gstNumber")
    pan_number: str | None = Field(default=None, alias="panNumber")
    company_registration_number: str | None = Field(default=None, alias="companyRegistrationNumber")
    address_line1: str | None = Field(default=None, alias="addressLine1")
    address_line2: str | None = Field(default=None, alias="addressLine2")
    city: str | None = None
    state: str | None = None
    country: str | None = None
    pincode: str | None = None
    website: str | None = None
    description: str | None = None
    bank_account_number: str | None = Field(default=None, alias="bankAccountNumber")
    ifsc_code: str | None = Field(default=None, alias="ifscCode")
    payment_terms: str | None = Field(default=None, alias="paymentTerms")


class VendorCreate(VendorPayload):
    pass


class VendorUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    category_id: int | None = Field(default=None, alias="categoryId")
    vendor_category: str | None = Field(default=None, alias="vendorCategory")
    company_name: str | None = Field(default=None, alias="companyName")
    contact_person_name: str | None = Field(default=None, alias="contactPersonName")
    designation: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = Field(default=None, alias="phoneNumber")
    alternate_phone: str | None = Field(default=None, alias="alternatePhone")
    gst_number: str | None = Field(default=None, alias="gstNumber")
    pan_number: str | None = Field(default=None, alias="panNumber")
    company_registration_number: str | None = Field(default=None, alias="companyRegistrationNumber")
    address_line1: str | None = Field(default=None, alias="addressLine1")
    address_line2: str | None = Field(default=None, alias="addressLine2")
    city: str | None = None
    state: str | None = None
    country: str | None = None
    pincode: str | None = None
    website: str | None = None
    description: str | None = None
    bank_account_number: str | None = Field(default=None, alias="bankAccountNumber")
    ifsc_code: str | None = Field(default=None, alias="ifscCode")
    payment_terms: str | None = Field(default=None, alias="paymentTerms")


class VendorCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    description: str | None = None
    is_active: bool | None = Field(default=None, alias="isActive")
