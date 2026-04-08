from pydantic import BaseModel, EmailStr, field_validator
import re

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UpdateProfileRequest(BaseModel):
    full_name: str
    phone: str

    @field_validator("phone")
    def validate_phone(cls, v):
        if not re.match(r'^[6-9][0-9]{9}$', v):
            raise ValueError("Invalid phone number")
        return v