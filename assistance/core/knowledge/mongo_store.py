from datetime import datetime
import uuid
from typing import Any
import re

import motor.motor_asyncio
from pymongo import DESCENDING, ASCENDING, IndexModel

from core.config import settings
from utils.logger import get_logger

logger = get_logger("mongo_store")


def _normalize_knowledge_content(content: str) -> str:
    """Normalize knowledge text so repeated facts can be matched reliably."""
    normalized = content.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


class MongoStore:
    """
    Structured persistent storage for NuraAgent.
    """

    def __init__(self):
        self._client = None
        self._db = None

    async def init(self):
        logger.info("Connecting to MongoDB", uri=settings.mongo.uri)
        self._client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo.uri)
        self._db = self._client[settings.mongo.db_name]
        await self._create_indexes()
        logger.info("MongoDB ready", db=settings.mongo.db_name)

    async def _create_indexes(self):
        # ChatHistory
        await self._db[settings.mongo.collection_chat_history].create_indexes([
            IndexModel([("session_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
        ])
        
        # KnowledgeBase
        await self._db[settings.mongo.collection_knowledge].create_indexes([
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("category", ASCENDING)]),
            IndexModel([("tags", ASCENDING)]),
            IndexModel([("user_id", ASCENDING), ("category", ASCENDING), ("content_normalized", ASCENDING)]),
        ])
        
        # Sessions
        await self._db[settings.mongo.collection_sessions].create_indexes([
            IndexModel([("session_id", ASCENDING)], unique=True),
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
        ])

    # ── Conversations (ChatHistory) ──────────────────────────────────────────

    async def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: dict | None = None,
    ) -> str:
        doc = {
            "session_id": session_id,
            "user_id": settings.nura.user_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
        }
        result = await self._db[settings.mongo.collection_chat_history].insert_one(doc)
        return str(result.inserted_id)

    async def get_session_history(self, session_id: str, limit: int = 20) -> list[dict]:
        cursor = (
            self._db[settings.mongo.collection_chat_history]
            .find(
                {"session_id": session_id},
                {"_id": 0, "role": 1, "content": 1, "created_at": 1},
            )
            .sort("created_at", ASCENDING)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def get_chat_history_paginated(
        self, 
        session_id: str, 
        page_size: int = 20, 
        current_page: int = 1
    ) -> dict:
        skip = (current_page - 1) * page_size
        query = {"session_id": session_id}
        
        total_chat = await self._db[settings.mongo.collection_chat_history].count_documents(query)
        
        cursor = (
            self._db[settings.mongo.collection_chat_history]
            .find(query, {"_id": 0})
            .sort("created_at", DESCENDING)
            .skip(skip)
            .limit(page_size)
        )
        chats = await cursor.to_list(length=page_size)
        
        return {
            "chats": chats,
            "totalChat": total_chat,
            "currentpage": current_page
        }

    async def get_recent_sessions(self, user_id: str | None = None, limit: int = 10) -> list[dict]:
        """Get sessions from the Sessions collection."""
        query = {}
        if user_id:
            query["user_id"] = user_id
        
        cursor = (
            self._db[settings.mongo.collection_sessions]
            .find(query, {"_id": 0})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    # ── Knowledge (KnowledgeBase) ───────────────────────────────────────────

    async def save_knowledge(
        self,
        content: str,
        category: str,
        tags: list[str] | None = None,
        source_session: str | None = None,
        chroma_id: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        normalized = _normalize_knowledge_content(content)
        doc = {
            "user_id": settings.nura.user_id,
            "content": content,
            "content_normalized": normalized,
            "category": category,
            "tags": tags or [],
            "source_session": source_session,
            "chroma_id": chroma_id,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
        }
        result = await self._db[settings.mongo.collection_knowledge].insert_one(doc)
        return str(result.inserted_id)

    async def find_existing_knowledge(
        self,
        content: str,
        category: str,
    ) -> dict | None:
        normalized = _normalize_knowledge_content(content)
        existing = await self._db[settings.mongo.collection_knowledge].find_one(
            {
                "user_id": settings.nura.user_id,
                "category": category,
                "content_normalized": normalized,
            },
            {"_id": 0, "content": 1, "category": 1, "chroma_id": 1, "created_at": 1},
        )
        if existing:
            return existing

        escaped = re.escape(content.strip())
        legacy = await self._db[settings.mongo.collection_knowledge].find_one(
            {
                "user_id": settings.nura.user_id,
                "category": category,
                "content": {"$regex": f"^\\s*{escaped}\\s*$", "$options": "i"},
            },
            {"_id": 1, "content": 1, "category": 1, "chroma_id": 1, "created_at": 1},
        )
        if legacy and legacy.get("_id"):
            await self._db[settings.mongo.collection_knowledge].update_one(
                {"_id": legacy["_id"]},
                {"$set": {"content_normalized": normalized}},
            )
            legacy.pop("_id", None)
        return legacy

    async def get_all_knowledge(self, limit: int = 100) -> list[dict]:
        cursor = (
            self._db[settings.mongo.collection_knowledge]
            .find({"user_id": settings.nura.user_id}, {"_id": 0})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def get_knowledge_by_category(self, category: str, limit: int = 20) -> list[dict]:
        cursor = (
            self._db[settings.mongo.collection_knowledge]
            .find({"user_id": settings.nura.user_id, "category": category}, {"_id": 0})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    # ── User (Users) ───────────────────────────────────────────────────────────

    async def update_profile(self, updates: dict[str, Any]):
        await self._db[settings.mongo.collection_users].update_one(
            {"user_id": settings.nura.user_id},
            {
                "$set": {**updates, "updated_at": datetime.utcnow()},
                "$setOnInsert": {
                    "user_id": settings.nura.user_id,
                    "created_at": datetime.utcnow(),
                },
            },
            upsert=True,
        )

    async def get_profile(self) -> dict:
        doc = await self._db[settings.mongo.collection_users].find_one(
            {"user_id": settings.nura.user_id}, {"_id": 0}
        )
        return doc or {}

    # ── Session (Sessions) ──────────────────────────────────────────────────

    async def create_session(self, title: str, user_id: str, session_id: str | None = None) -> dict:
        sid = session_id or str(uuid.uuid4())
        doc = {
            "id": sid,
            "session_id": sid,
            "title": title,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await self._db[settings.mongo.collection_sessions].insert_one(doc)
        if "_id" in doc:
            del doc["_id"]
        return doc

    async def upsert_session(self, session_id: str, data: dict):
        await self._db[settings.mongo.collection_sessions].update_one(
            {"session_id": session_id},
            {
                "$set": {**data, "updated_at": datetime.utcnow()},
                "$setOnInsert": {
                    "session_id": session_id,
                    "user_id": settings.nura.user_id,
                    "created_at": datetime.utcnow(),
                },
            },
            upsert=True,
        )

    async def close(self):
        if self._client:
            self._client.close()
# Singleton
mongo_store = MongoStore()
