import json
import uuid
from typing import AsyncGenerator
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse

from agents.orchestrator import nura
from models.request.chat_request import ChatRequest
from models.response.chat_response import ChatResponse
from utils.logger import get_logger

logger = get_logger("agent_api")

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        result = await nura.chat(
            message=req.message,
            session_id=req.session_id,
        )
        return ChatResponse(**result)
    except Exception as e:
        logger.error("Chat error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """Server-Sent Events streaming."""
    sid = req.session_id or str(uuid.uuid4())

    async def generate() -> AsyncGenerator[str, None]:
        try:
            async for chunk in nura.stream(message=req.message, session_id=sid):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info("WebSocket connected", session=session_id[:8])

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "").strip()

            if not message:
                await websocket.send_json({"type": "error", "content": "Empty message"})
                continue

            async for event in nura.stream(message=message, session_id=session_id):
                await websocket.send_json(event)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", session=session_id[:8])
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
