import uuid
from datetime import datetime
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaConfig
from langchain_ollama import OllamaEmbeddings

from core.config import settings
from utils.logger import get_logger

logger = get_logger("chroma_store")


class ChromaStore:
    """
    Semantic vector store — the brain behind Nura's memory recall.

    Two collections:
      nura_knowledge      : facts, preferences, decisions, goals
      nura_conversations  : summaries of past sessions
    """

    def __init__(self):
        self._client = None
        self._knowledge_col = None
        self._conversations_col = None
        self._embeddings = None

    async def init(self):
        logger.info("Initialising ChromaDB", path=settings.chroma.persist_dir)

        self._client = chromadb.PersistentClient(
            path=settings.chroma.persist_dir,
            settings=ChromaConfig(anonymized_telemetry=False),
        )
        self._knowledge_col = self._client.get_or_create_collection(
            name=settings.chroma.collection_knowledge,
            metadata={"hnsw:space": "cosine"},
        )
        self._conversations_col = self._client.get_or_create_collection(
            name=settings.chroma.collection_conversations,
            metadata={"hnsw:space": "cosine"},
        )
        self._embeddings = OllamaEmbeddings(
            base_url=settings.ollama.base_url,
            model=settings.ollama.embed_model,
        )

        logger.info(
            "ChromaDB ready",
            knowledge_docs=self._knowledge_col.count(),
            conversation_docs=self._conversations_col.count(),
        )

    def _embed(self, text: str) -> list[float]:
        return self._embeddings.embed_query(text)

    def _clean_meta(self, meta: dict) -> dict:
        """ChromaDB only allows str/int/float/bool in metadata."""
        return {
            k: str(v) if not isinstance(v, (str, int, float, bool)) else v
            for k, v in meta.items()
        }

    def _build_where(self, **conditions: Any) -> dict:
        """Build a Chroma-compatible where filter for one or more equality conditions."""
        active_conditions = [
            {key: value}
            for key, value in conditions.items()
            if value is not None
        ]
        if not active_conditions:
            return {}
        if len(active_conditions) == 1:
            return active_conditions[0]
        return {"$and": active_conditions}

    # ── Knowledge collection ──────────────────────────────────────────────────

    async def add_knowledge(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
        doc_id: str | None = None,
    ) -> str:
        doc_id = doc_id or str(uuid.uuid4())
        meta = self._clean_meta({
            "user_id": settings.nura.user_id,
            "created_at": datetime.utcnow().isoformat(),
            "source": "conversation",
            **(metadata or {}),
        })
        self._knowledge_col.add(
            ids=[doc_id],
            documents=[content],
            embeddings=[self._embed(content)],
            metadatas=[meta],
        )
        logger.debug("Knowledge stored", id=doc_id, preview=content[:80])
        return doc_id

    async def search_knowledge(
        self,
        query: str,
        n_results: int = 5,
        category: str | None = None,
    ) -> list[dict]:
        total = self._knowledge_col.count()
        if total == 0:
            return []

        where = self._build_where(
            user_id=settings.nura.user_id,
            category=category,
        )

        results = self._knowledge_col.query(
            query_embeddings=[self._embed(query)],
            n_results=min(n_results, total),
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                hits.append({
                    "id": doc_id,
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": round(1 - results["distances"][0][i], 3),
                })
        return hits

    async def find_similar_knowledge(
        self,
        content: str,
        category: str,
        n_results: int | None = None,
    ) -> list[dict]:
        """Return same-category knowledge hits ordered by semantic similarity."""
        limit = n_results or settings.chroma.semantic_duplicate_candidates
        return await self.search_knowledge(
            query=content,
            n_results=limit,
            category=category,
        )

    # ── Conversations collection ──────────────────────────────────────────────

    async def add_conversation_summary(
        self,
        session_id: str,
        summary: str,
        metadata: dict | None = None,
    ) -> str:
        doc_id = f"conv_{session_id}"
        meta = self._clean_meta({
            "user_id": settings.nura.user_id,
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            **(metadata or {}),
        })
        # Upsert — delete old, add new
        try:
            self._conversations_col.delete(ids=[doc_id])
        except Exception:
            pass

        self._conversations_col.add(
            ids=[doc_id],
            documents=[summary],
            embeddings=[self._embed(summary)],
            metadatas=[meta],
        )
        return doc_id

    async def search_conversations(self, query: str, n_results: int = 3) -> list[dict]:
        total = self._conversations_col.count()
        if total == 0:
            return []

        results = self._conversations_col.query(
            query_embeddings=[self._embed(query)],
            n_results=min(n_results, total),
            where=self._build_where(user_id=settings.nura.user_id),
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                hits.append({
                    "id": doc_id,
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": round(1 - results["distances"][0][i], 3),
                })
        return hits

    @property
    def knowledge_count(self) -> int:
        return self._knowledge_col.count() if self._knowledge_col else 0

    @property
    def conversation_count(self) -> int:
        return self._conversations_col.count() if self._conversations_col else 0

    @property
    def is_ready(self) -> bool:
        return self._client is not None


# Singleton
chroma_store = ChromaStore()
