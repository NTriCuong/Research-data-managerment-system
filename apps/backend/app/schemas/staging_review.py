from pydantic import BaseModel, Field


class RequestRevisionRequest(BaseModel):
    note: str = Field(min_length=1, max_length=1000)


class ForwardToApprovalRequest(BaseModel):
    note: str | None = Field(default=None, max_length=1000)
