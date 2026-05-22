from pydantic import BaseModel, EmailStr, field_validator
import re

# ── Request schemas ───────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

# ── Response schemas ──────────────────────────────────────────────────────────

class LoginResponse(BaseModel):
    """hybrid approach: access token trong response body, refresh token trong HTTPOnly Cookie"""
    access_token: str
    token_type: str = "bearer"
    id: str
    email: str
    full_name: str
    user_code: str
    role: str          # role name, không phải id
    is_active: bool

class AccessTokenResponse(BaseModel):
    """Trả về sau /refresh — chỉ cấp lại access token."""
    access_token: str
    token_type: str = "bearer"

class UserMeResponse(BaseModel): 
    """Thông tin user hiện tại — trả về từ /me."""
    id: str
    email: str
    full_name: str
    user_code: str
    role: str          # role name, không phải id
    is_active: bool

    model_config = {"from_attributes": True}