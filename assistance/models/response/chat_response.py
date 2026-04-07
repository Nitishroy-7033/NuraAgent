from pydantic import BaseModel

class ChatResponse(BaseModel):
    response: str
    intent: str
    agent: str
    session_id: str
    error: str = ""
