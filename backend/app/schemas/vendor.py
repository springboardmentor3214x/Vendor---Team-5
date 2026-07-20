from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class VendorCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool


class VendorContactCreate(BaseModel):
    contact_person_name: str
    designation: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    is_primary: bool = False


class VendorContactOut(VendorContactCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vendor_id: int


class VendorCreate(BaseModel):
    company_name: str
    category_id: int
    contact_person_name: str
    designation: Optional[str] = None
    email: str
    phone_number: str
    alternate_phone: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    company_registration_number: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    bank_account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    payment_terms: Optional[str] = None


class VendorUpdate(BaseModel):
    company_name: Optional[str] = None
    category_id: Optional[int] = None
    contact_person_name: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    alternate_phone: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    company_registration_number: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    bank_account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    payment_terms: Optional[str] = None


class VendorOut(VendorCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vendor_status: str
    approval_status: str
    reliability_score: float
    created_at: datetime
    updated_at: datetime
    category: Optional[VendorCategoryOut] = None