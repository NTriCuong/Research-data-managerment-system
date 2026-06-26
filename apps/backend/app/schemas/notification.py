from pydantic import BaseModel

class RegisterTokenRequest(BaseModel):
    fcm_token: str
    device_name: str | None = None