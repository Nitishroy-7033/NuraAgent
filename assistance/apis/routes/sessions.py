from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from core.knowledge.mongo_store import mongo_store
from models.request.session_request import SessionCreateRequest
from models.response.history_response import ChatHistoryResponse
from utils.logger import get_logger

logger = get_logger("sessions_api")

router = APIRouter(tags=["sessions"])

@router.post("/sessions")
async def create_session(req: SessionCreateRequest):
    try:
        session = await mongo_store.create_session(
            title=req.title,
            user_id=req.userId
        )
        return session
    except Exception as e:
        logger.error("Create session error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_sessions(userId: Optional[str] = None, limit: int = 20):
    try:
        sessions = await mongo_store.get_recent_sessions(user_id=userId, limit=limit)
        return {"sessions": sessions}
    except Exception as e:
        logger.error("Get sessions error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat-history", response_model=ChatHistoryResponse)
async def get_chat_history(
    sessionid: str,
    pagesize: int = 20,
    currentpage: int = 1
):
    try:
        history = await mongo_store.get_chat_history_paginated(
            session_id=sessionid,
            page_size=pagesize,
            current_page=currentpage
        )
        return ChatHistoryResponse(**history)
    except Exception as e:
        logger.error("Get chat history error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
