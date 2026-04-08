import json
import re

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

from core.config import config
from core.knowledge.chroma_store import chroma_store
from core.knowledge.mongo_store import mongo_store
from utils.logger import get_logger
from utils.prompts import KNOWLEDGE_EXTRACTOR_AGENT_PROMPT

logger = get_logger("knowledge_extractor_agent")

# Category mapping: JSON field → MongoDB category label
_CATEGORY_MAP = {
    "facts":        "fact",
    "preferences":  "preference",
    "professional": "professional",
    "decisions":    "decision",
    "goals":        "goal",
    "people":       "person",
    "events":       "event",
}


def _render_extractor_prompt(user_message: str, assistant_response: str) -> str:
    """Render the extractor prompt without interpreting literal JSON braces."""
    return (
        KNOWLEDGE_EXTRACTOR_AGENT_PROMPT
        .replace("{user_message}", user_message)
        .replace("{assistant_response}", assistant_response)
    )


def _parse_json(text: str) -> dict | None:
    """Robustly extract a JSON object from LLM output."""
    text = text.strip()
    
    # Try 1: direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try 2: strip markdown fences
    if "```" in text:
        for part in text.split("```"):
            part = part.strip()
            if part.startswith("json"):
                part = part[4:]
            try:
                return json.loads(part.strip())
            except Exception:
                continue

    # Try 3: find first {...} block
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    # Try 4: if it looks like partial JSON starting with a key, wrap in {}
    if text.startswith('"') and ':' in text:
        try:
            wrapped = '{' + text + '}'
            return json.loads(wrapped)
        except Exception:
            pass

    return None


def _has_valid_knowledge_items(extracted: dict) -> bool:
    """Return true if extracted JSON contains real knowledge items worth storing."""
    placeholder_signals = [
        "Factual info about the user",
        "Likes, dislikes, habits",
        "Job title",
        "Company",
        "Things user decided",
        "Goals, ambitions, plans",
        "People mentioned",
        "Events, dates, appointments",
        "First-person confirmation",
        "empty string if nothing found",
    ]

    for field in _CATEGORY_MAP.keys():
        items = extracted.get(field, [])
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, str):
                continue
            text = item.strip()
            if len(text) < 8:
                continue
            if any(signal in text for signal in placeholder_signals):
                continue
            return True
    return False


class KnowledgeExtractorAgent:
    """Dedicated async agent for post-conversation knowledge extraction."""

    def __init__(self):
        self._llm: ChatOllama | None = None

    def _get_llm(self) -> ChatOllama:
        """Lazy-init LLM — only created when first needed."""
        if self._llm is None:
            self._llm = ChatOllama(
                base_url=config.ollama.base_url,
                model=config.ollama.knowledge_extractor_model,
                temperature=0.1,  # low temp for accurate extraction
            )
        return self._llm

    async def run(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
    ) -> None:
        """
        Main entry point. Runs the full extraction pipeline.
        Always called as a background task — never awaited by the caller.
        """
        logger.debug(
            "Knowledge extractor started",
            session=session_id[:8],
        )

        try:
            # ── Step 1: Extract ───────────────────────────────────────────────
            extracted = await self._extract(user_message, assistant_response, session_id)
            if extracted is None:
                logger.debug("Extractor: no valid JSON returned, skipping")
                return

            should_store = extracted.get("should_store", False)
            if not should_store:
                if _has_valid_knowledge_items(extracted):
                    logger.warning(
                        "Extractor returned should_store=false with valid items; overriding to true",
                        session=session_id[:8],
                        extracted=extracted,
                    )
                    should_store = True
                else:
                    logger.debug("Extractor: nothing worth storing in this turn")
                    return

            if should_store and not _has_valid_knowledge_items(extracted):
                logger.warning(
                    "Extractor returned should_store=true but no valid items found; skipping",
                    session=session_id[:8],
                    extracted=extracted,
                )
                return

            # ── Step 2: Confirm ───────────────────────────────────────────────
            confirmation = extracted.get("confirmation", "").strip()
            if confirmation:
                logger.info(
                    "Memory Agent confirmation",
                    session=session_id[:8],
                    confirmation=confirmation,
                )

            # ── Step 3: Store ─────────────────────────────────────────────────
            stored_count = await self._store(extracted, session_id)

            # Also store a conversation summary in ChromaDB for semantic recall
            if confirmation:
                await chroma_store.add_conversation_summary(
                    session_id=session_id,
                    summary=confirmation,
                )

            logger.info(
                "Knowledge extractor done",
                session=session_id[:8],
                stored_count=stored_count,
                confirmation=confirmation[:100] if confirmation else "—",
            )

        except Exception as e:
            logger.warning(
                "Knowledge extractor failed",
                session=session_id[:8],
                error=str(e),
            )

    async def _extract(self, user_message: str, assistant_response: str, session_id: str) -> dict | None:
        """Step 1 — Ask LLM to extract structured knowledge from the conversation."""
        prompt = _render_extractor_prompt(user_message, assistant_response)
        llm = self._get_llm()
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        raw = response.content.strip()
        logger.debug(
            "Knowledge extractor raw response",
            session=session_id[:8],
            raw=raw,
        )
        extracted = _parse_json(raw)

        if extracted is None:
            logger.debug("Extractor: could not parse JSON", raw_preview=raw[:200])
        else:
            logger.info(
                "Knowledge extractor response",
                session=session_id[:8],
                extracted=extracted,
            )
        return extracted

    async def _store(self, extracted: dict, session_id: str) -> int:
        """Step 3 — Store all found items to MongoDB + ChromaDB."""
        stored_count = 0

        for field, category in _CATEGORY_MAP.items():
            items = extracted.get(field, [])
            if not isinstance(items, list):
                continue

            for item in items:
                if not item or not isinstance(item, str) or len(item.strip()) < 8:
                    continue

                item = item.strip()

                # Store in ChromaDB for semantic search
                chroma_id = await chroma_store.add_knowledge(
                    content=item,
                    metadata={
                        "category": category,
                        "session_id": session_id,
                        "source": "knowledge_extractor_agent",
                    },
                )

                # Store in MongoDB for structured browsing
                await mongo_store.save_knowledge(
                    content=item,
                    category=category,
                    source_session=session_id,
                    chroma_id=chroma_id,
                    metadata={"source": "knowledge_extractor_agent"},
                )

                stored_count += 1

        return stored_count


# Singleton — import this everywhere
knowledge_extractor_agent = KnowledgeExtractorAgent()
