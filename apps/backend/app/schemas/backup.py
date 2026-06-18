from datetime import datetime

from pydantic import BaseModel


class BackupOut(BaseModel):
    filename: str
    size_bytes: int
    created_at: datetime
