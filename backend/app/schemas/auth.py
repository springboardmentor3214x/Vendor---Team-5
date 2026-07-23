from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")
    full_name: str = Field(alias="fullName")
    email: EmailStr
    password: str
    role: str


class UserLogin(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, extra="ignore")
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool = True

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str