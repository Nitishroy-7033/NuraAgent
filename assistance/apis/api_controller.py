"""
api_controller.py — Nura's FastAPI backend

Endpoints:
  GET  /health
  POST /chat              standard request/response
  POST /chat/stream       server-sent events streaming
  WS   /ws/{session_id}  WebSocket streaming

  POST /knowledge/store
  POST /knowledge/search
  GET  /knowledge/all
  GET  /knowledge/category/{category}

  GET  /sessions
  GET  /sessions/{session_id}/history
  GET  /profile
"""
import json
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agents.orchestrator import nura
from core.config import config
from core.knowledge.knowledge_service import knowledge_service
from core.knowledge.mongo_store import mongo_store
from utils.logger import get_logger

logger = get_logger("api")


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Nura API starting...")
    await nura.init()
    logger.info("Nura API ready")
    yield
    logger.info("Nura API shutting down...")
    await mongo_store.close()


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Nura API",
    description=f"Personal AI assistant for {config.user_name}",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None
    history: list[dict] | None = None


class ChatResponse(BaseModel):
    response: str
    intent: str
    agent: str
    session_id: str
    error: str = ""


class KnowledgeStoreRequest(BaseModel):
    content: str = Field(..., min_length=1)
    category: str = "fact"
    tags: list[str] = Field(default_factory=list)


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    n_results: int = 5


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "user": config.user_name,
        "model": config.ollama.chat_model,
    }


# ── Chat ──────────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        result = await nura.chat(
            message=req.message,
            session_id=req.session_id,
            history=req.history,
        )
        return ChatResponse(**result)
    except Exception as e:
        logger.error("Chat error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
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


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    Client sends:  {"message": "..."}
    Server sends:
      {"type": "start"}
      {"type": "chunk", "content": "..."}
      {"type": "done",  "intent": "...", "agent": "..."}
      {"type": "error", "content": "..."}
    """
    await websocket.accept()
    logger.info("WebSocket connected", session=session_id[:8])

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", "").strip()

            if not message:
                await websocket.send_json({"type": "error", "content": "Empty message"})
                continue

            await websocket.send_json({"type": "start", "session_id": session_id})

            async for event in nura.stream(message=message, session_id=session_id):
                await websocket.send_json(event)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", session=session_id[:8])
    except Exception as e:
        logger.error("WebSocket error", error=str(e))


# ── Knowledge ─────────────────────────────────────────────────────────────────

@app.post("/knowledge/store")
async def store_knowledge(req: KnowledgeStoreRequest):
    chroma_id = await knowledge_service.store_explicit(
        content=req.content,
        category=req.category,
        tags=req.tags,
    )
    return {"status": "stored", "id": chroma_id}


@app.post("/knowledge/search")
async def search_knowledge(req: KnowledgeSearchRequest):
    from core.knowledge.chroma_store import chroma_store
    results = await chroma_store.search_knowledge(req.query, n_results=req.n_results)
    return {"results": results, "count": len(results)}


@app.get("/knowledge/all")
async def get_all_knowledge(limit: int = 50):
    items = await mongo_store.get_all_knowledge(limit=limit)
    return {"items": items, "count": len(items)}


@app.get("/knowledge/category/{category}")
async def get_by_category(category: str, limit: int = 20):
    items = await mongo_store.get_knowledge_by_category(category=category, limit=limit)
    return {"items": items, "count": len(items)}


# ── Sessions ──────────────────────────────────────────────────────────────────

@app.get("/sessions")
async def get_sessions(limit: int = 10):
    sessions = await mongo_store.get_recent_sessions(limit=limit)
    return {"sessions": sessions}


@app.get("/sessions/{session_id}/history")
async def get_history(session_id: str, limit: int = 20):
    history = await mongo_store.get_session_history(session_id=session_id, limit=limit)
    return {"history": history, "session_id": session_id}


# ── Profile ───────────────────────────────────────────────────────────────────

@app.get("/profile")
async def get_profile():
    return await mongo_store.get_profile()


@app.patch("/profile")
async def update_profile(updates: dict):
    await mongo_store.update_profile(updates)
    return {"status": "updated"}