from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import json
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
    thread_id: Optional[str] = None

@app.get("/health")
async def health_check():
    return {
        "status":"ok",
        "message":"Assistance API is running",
        "service":"Assistance API",
        "version":"1.0",
        "author":"Nitish Kumar"
    }

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    logger.info(f"Received streaming chat request: {request.query}")
    async def event_generator():
        try:
            async for chunk in chat_service.stream_chat_completion(
                request.query, 
                request.thread_id
            ):
                await asyncio.sleep(0.01)
                yield f"data: {json.dumps({'text': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Error in stream: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
@app.post("/chat/completion")
async def chat_completion(request: ChatRequest):
    """
    Handles static chat completion requests asynchronously.
    """
    try:
        response_text = await chat_service.chat_completion(
            request.query, 
            request.thread_id
        )
        return {"response": response_text}
    except Exception as e:
        logger.error(f"Error in /chat/completion endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
