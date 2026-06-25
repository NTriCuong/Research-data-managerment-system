from pydantic import BaseModel
from uuid import UUID

class RegisterTokenRequest(BaseModel):
    user_id: UUID
    fcm_token: str
    device_name: str | None = None