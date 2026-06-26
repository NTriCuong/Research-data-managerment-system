from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: UUID
    recipient_user_id: UUID
    actor_user_id: UUID | None = None
    event_type: str
    title: str
    message: str
    target_url: str | None = None
    payload: dict | None = None
    read_at: datetime | None = None
    created_at: datetime


class RegisterTokenRequest(BaseModel):
    fcm_token: str
    device_name: str | None = None
