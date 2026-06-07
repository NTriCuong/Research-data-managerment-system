from pydantic import BaseModel


class IncomingFile(BaseModel):
    filename: str
    content_type: str
    content: bytes
