from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from utils.logger import setup_logger
from core.chat.chat_service import ChatService

logger = setup_logger("api_controller")
app = FastAPI(
    title="Assistance API", 
    version="1.0"
)

# Initialize ChatService instance
chat_service = ChatService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    system_prompt: Optional[str] = None
    thread_id: Optional[str] = None
    stream: bool = True

@app.get("/health")
async def health_check():
    return {
        "status":"ok",
        "message":"Assistance API is running",
        "service":"Assistance API",
        "version":"1.0",
        "author":"Nitish Kumar"
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Handles chat requests and returns either a streaming or static response.
    """
    try:
        if request.stream:
            return StreamingResponse(
                chat_service.stream_chat_completion(
                    request.query, 
                    request.system_prompt, 
                    request.thread_id
                ),
                media_type="text/plain"
            )
        else:
            response_text = chat_service.chat_completion(
                request.query, 
                request.system_prompt, 
                request.thread_id
            )
            return {"response": response_text}
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
