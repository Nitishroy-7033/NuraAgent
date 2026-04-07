from pydantic import BaseModel
from typing import List, Dict, Any

class ChatHistoryResponse(BaseModel):
    chats: List[Dict[str, Any]]
    totalChat: int
    currentpage: int
