from pydantic import BaseModel
from typing import Optional

class SessionCreateRequest(BaseModel):
    title: str
    userId: str
