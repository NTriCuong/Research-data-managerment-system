from pydantic import BaseModel, EmailStr, field_validator
import re

# Request schemas 

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Response schemas 

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id: str
    email: str
    full_name: str
    user_code: str
    role: str          
    is_active: bool

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserMeResponse(BaseModel): 
    id: str
    email: str
    full_name: str
    user_code: str
    role: str          
    is_active: bool

    model_config = {"from_attributes": True}