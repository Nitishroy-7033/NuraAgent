from datetime import datetime
from typing import Any

import motor.motor_asyncio
from pymongo import DESCENDING, ASCENDING, IndexModel

from core.config import settings
from utils.logger import get_logger

logger = get_logger("mongo_store")


class MongoStore:
    """
    Structured persistent storage for Nura.

    Collections:
      conversations  — full message history per session
      knowledge      — facts, decisions, preferences, goals
      sessions       — session metadata
      user_profile   — Nitish's evolving profile
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
        await self._db.conversations.create_indexes([
            IndexModel([("session_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
        ])
        await self._db.knowledge.create_indexes([
            IndexModel([("user_id", ASCENDING), ("created_at", DESCENDING)]),
            IndexModel([("category", ASCENDING)]),
            IndexModel([("tags", ASCENDING)]),
        ])
        await self._db.sessions.create_indexes([
            IndexModel([("session_id", ASCENDING)], unique=True),
        ])

    # ── Conversations ─────────────────────────────────────────────────────────

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
        result = await self._db.conversations.insert_one(doc)
        return str(result.inserted_id)

    async def get_session_history(self, session_id: str, limit: int = 20) -> list[dict]:
        cursor = (
            self._db.conversations
            .find(
                {"session_id": session_id},
                {"_id": 0, "role": 1, "content": 1, "created_at": 1},
            )
            .sort("created_at", ASCENDING)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def get_recent_sessions(self, limit: int = 10) -> list[dict]:
        pipeline = [
            {"$match": {"user_id": settings.nura.user_id}},
            {"$sort": {"created_at": -1}},
            {"$group": {
                "_id": "$session_id",
                "last_message": {"$first": "$content"},
                "last_role": {"$first": "$role"},
                "last_at": {"$first": "$created_at"},
                "message_count": {"$sum": 1},
            }},
            {"$sort": {"last_at": -1}},
            {"$limit": limit},
        ]
        return await self._db.conversations.aggregate(pipeline).to_list(length=limit)

    # ── Knowledge ─────────────────────────────────────────────────────────────

    async def save_knowledge(
        self,
        content: str,
        category: str,
        tags: list[str] | None = None,
        source_session: str | None = None,
        chroma_id: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        doc = {
            "user_id": settings.nura.user_id,
            "content": content,
            "category": category,   # fact | preference | decision | goal | project | person
            "tags": tags or [],
            "source_session": source_session,
            "chroma_id": chroma_id,
            "metadata": metadata or {},
            "created_at": datetime.utcnow(),
        }
        result = await self._db.knowledge.insert_one(doc)
        return str(result.inserted_id)

    async def get_all_knowledge(self, limit: int = 100) -> list[dict]:
        cursor = (
            self._db.knowledge
            .find({"user_id": settings.nura.user_id}, {"_id": 0})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def get_knowledge_by_category(self, category: str, limit: int = 20) -> list[dict]:
        cursor = (
            self._db.knowledge
            .find({"user_id": settings.nura.user_id, "category": category}, {"_id": 0})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    # ── User profile ──────────────────────────────────────────────────────────

    async def update_profile(self, updates: dict[str, Any]):
        await self._db.user_profile.update_one(
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
        doc = await self._db.user_profile.find_one(
            {"user_id": settings.nura.user_id}, {"_id": 0}
        )
        return doc or {}

    # ── Session ───────────────────────────────────────────────────────────────

    async def upsert_session(self, session_id: str, data: dict):
        await self._db.sessions.update_one(
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