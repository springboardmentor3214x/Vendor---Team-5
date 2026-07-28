from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


ALLOWED_ROLES = {
    "Administrator",
    "Procurement Manager",
    "Supply Chain Manager",
    "Vendor",
    "Finance Officer",
    "Auditor",
}


class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    full_name: str = Field(alias="fullName", min_length=2, max_length=150)
    employee_id: Optional[str] = Field(default=None, alias="employeeId")
    company_name: Optional[str] = Field(default=None, alias="companyName")
    email: EmailStr
    mobile_number: Optional[str] = Field(default=None, alias="mobileNumber")
    password: str = Field(min_length=8)
    confirm_password: str = Field(alias="confirmPassword", min_length=8)
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in ALLOWED_ROLES:
            raise ValueError("Invalid role selected")
        return value

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        cleaned = value.strip()
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError("Mobile number must be between 10 and 15 digits")
        return cleaned

    @field_validator("company_name")
    @classmethod
    def validate_company_name_for_vendor(cls, value: Optional[str], info) -> Optional[str]:
        role = info.data.get("role")
        if role == "Vendor" and not value:
            raise ValueError("Company name is required for Vendor role")
        return value

    @field_validator("employee_id")
    @classmethod
    def validate_employee_id_for_internal_users(cls, value: Optional[str], info) -> Optional[str]:
        role = info.data.get("role")
        if role and role != "Vendor" and not value:
            raise ValueError("Employee ID is required for internal users")
        return value


class UserLogin(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    email: EmailStr
    password: str = Field(min_length=1)


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    full_name: Optional[str] = Field(default=None, alias="fullName", min_length=2, max_length=150)
    mobile_number: Optional[str] = Field(default=None, alias="mobileNumber")
    company_name: Optional[str] = Field(default=None, alias="companyName")
    profile_picture: Optional[str] = Field(default=None, alias="profilePicture")

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        cleaned = value.strip()
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError("Mobile number must be between 10 and 15 digits")
        return cleaned


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    full_name: str = Field(alias="fullName")
    employee_id: Optional[str] = Field(default=None, alias="employeeId")
    company_name: Optional[str] = Field(default=None, alias="companyName")
    email: EmailStr
    mobile_number: Optional[str] = Field(default=None, alias="mobileNumber")
    role: str
    is_active: bool = Field(default=True, alias="isActive")
    profile_picture: Optional[str] = Field(default=None, alias="profilePicture")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Optional[str] = None
    redirect_to: Optional[str] = Field(default=None, alias="redirectTo")


class MessageResponse(BaseModel):
    message: str
    reset_token: Optional[str] = Field(default=None, alias="resetToken")


class ForgotPasswordRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    token: str
    new_password: str = Field(alias="newPassword", min_length=8)
    confirm_password: str = Field(alias="confirmPassword", min_length=8)


class PasswordChangeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")

    current_password: str = Field(alias="currentPassword", min_length=1)
    new_password: str = Field(alias="newPassword", min_length=8)
    confirm_password: str = Field(alias="confirmPassword", min_length=8)