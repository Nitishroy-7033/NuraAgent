from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import uvicorn
import os
import sys

# Add root to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.chat_agent import ChatAgent
from utils.logger import setup_logger

logger = setup_logger("api")
app = FastAPI(title="NuraAgent API")

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared agent instance for now (session management can be added later)
agent = ChatAgent()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"status": "online", "message": "NuraAgent API is running"}

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming endpoint for the Chat Agent.
    Yields chunks of text in Server-Sent Events (SSE) format.
    """
    logger.info(f"Received stream request: {request.message[:50]}...")

    async def event_generator():
        try:
            # agent.run is a sync generator, so we iterate through it
            # and yield chunks in SSE format.
            for chunk in agent.run(request.message):
                # Small yield to let event loop breathe (optional)
                await asyncio.sleep(0.01)
                yield f"data: {json.dumps({'text': chunk})}\n\n"
            
            # Signal end of stream
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Error in stream: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/chat/clear")
async def clear_chat():
    """Clears the agent's chat history/session."""
    agent.reset()
    logger.info("Chat history cleared via API.")
    return {"status": "success", "message": "Memory cleared"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
