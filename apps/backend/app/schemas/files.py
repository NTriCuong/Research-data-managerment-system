from dataclasses import dataclass
from typing import BinaryIO


@dataclass(slots=True)
class IncomingFile:
    filename: str
    content_type: str
    fileobj: BinaryIO
