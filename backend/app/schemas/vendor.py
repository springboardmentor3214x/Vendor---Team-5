from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class VendorCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool


class VendorContactCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")
    contact_person_name: str = Field(alias="contactPerson")
    designation: Optional[str] = Field(default=None, alias="designation")
    email: Optional[str] = None
    phone_number: Optional[str] = Field(default=None, alias="phone")
    is_primary: bool = False


class VendorContactOut(VendorContactCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vendor_id: int


class VendorCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")
    company_name: str = Field(alias="companyName")
    category_id: int = Field(alias="categoryId")
    contact_person_name: str = Field(alias="contactPerson")
    designation: Optional[str] = Field(default=None, alias="designation")
    email: str
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


class VendorUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")
    company_name: Optional[str] = Field(default=None, alias="companyName")
    category_id: Optional[int] = Field(default=None, alias="categoryId")
    contact_person_name: Optional[str] = Field(default=None, alias="contactPerson")
    designation: Optional[str] = Field(default=None, alias="designation")
    email: Optional[str] = None
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


class VendorOut(VendorCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vendor_status: str
    approval_status: str
    reliability_score: float
    created_at: datetime
    updated_at: datetime
    category: Optional[VendorCategoryOut] = None