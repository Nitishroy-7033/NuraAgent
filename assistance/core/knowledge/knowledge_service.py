"""
knowledge_service.py — The brain of Nura's memory system

Three responsibilities:
  1. get_relevant_context()  → fetch memories before every agent response
  2. extract_and_store()     → auto-learn from every conversation turn (background)
  3. store_explicit()        → handle "remember that..." commands
"""
import asyncio
import json

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

from core.config import config
from core.knowledge.chroma_store import chroma_store
from core.knowledge.mongo_store import mongo_store
from utils.logger import get_logger
from utils.prompts import KNOWLEDGE_EXTRACT_PROMPT, KNOWLEDGE_QUERY_REWRITE_PROMPT

logger = get_logger("knowledge_service")

_SEMANTIC_DUPLICATE_JUDGE_PROMPT = """Decide whether these two memory statements mean the same thing about the user.

Category: {category}
Existing memory: {existing}
Candidate memory: {candidate}

Rules:
- Answer SAME if they express the same durable user fact, preference, decision, goal, person, project, professional detail, or event, even with different wording.
- Answer DIFFERENT if the candidate adds materially new information, changes the fact, or refers to a different thing.
- If the candidate is an update or correction of the existing memory, answer DIFFERENT.

Return only SAME or DIFFERENT."""


def _render_prompt(template: str, **values: str) -> str:
    """Render prompt placeholders without interpreting literal JSON braces."""
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace(f"{{{key}}}", value)
    return rendered


def _sanitize_rewritten_query(text: str, fallback: str) -> str:
    """Keep only the actual search query text returned by the rewrite model."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = lines[0] if lines else ""
    cleaned = cleaned.strip().strip("\"'")

    prefixes = (
        "search for ",
        "search query: ",
        "query: ",
        "find ",
        "look up ",
    )
    lowered = cleaned.lower()
    for prefix in prefixes:
        if lowered.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip(" :\"'")
            break

    return (cleaned or fallback).strip()[:200]



def _extract_json(text: str) -> dict | None:
    """
    Robustly extract a JSON object from LLM output.
    Handles: extra prose, markdown fences, partial wrapping.
    """
    import re as _re
    # Try 1: direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try 2: strip markdown fences
    cleaned = text
    if "```" in cleaned:
        parts = cleaned.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:]
            try:
                return json.loads(part.strip())
            except Exception:
                continue

    # Try 3: find first { ... } block in the text
    match = _re.search(r'\{.*?\}', text, _re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    return None


class KnowledgeService:

    def __init__(self):
        self._llm: ChatOllama | None = None

    # ── Startup ───────────────────────────────────────────────────────────────

    async def init(self):
        """Init both stores. Call once at app startup."""
        await chroma_store.init()
        await mongo_store.init()
        logger.info(
            "Knowledge service ready",
            knowledge_docs=chroma_store.knowledge_count,
            conversation_docs=chroma_store.conversation_count,
        )

    # ── LLM (lazy) ────────────────────────────────────────────────────────────

    def _get_llm(self) -> ChatOllama:
        """Lazy-init LLM — only created when first needed."""
        if self._llm is None:
            self._llm = ChatOllama(
                base_url=config.ollama.base_url,
                model=config.ollama.chat_model,
                temperature=0.1,   # low temp for accurate extraction
            )
        return self._llm

    async def find_duplicate_knowledge(
        self,
        content: str,
        category: str,
    ) -> dict | None:
        """Find an existing memory that should block this new write."""
        exact = await mongo_store.find_existing_knowledge(content=content, category=category)
        if exact:
            return {
                "reason": "exact",
                "score": 1.0,
                "existing": exact,
            }

        if not chroma_store.is_ready:
            return None

        candidates = await chroma_store.find_similar_knowledge(
            content=content,
            category=category,
            n_results=config.chroma.semantic_duplicate_candidates,
        )
        if not candidates:
            return None

        high_threshold = config.chroma.semantic_duplicate_high_threshold
        judge_threshold = config.chroma.semantic_duplicate_judge_threshold

        for hit in candidates:
            score = hit.get("score", 0.0)
            if score >= high_threshold:
                return {
                    "reason": "semantic_high_confidence",
                    "score": score,
                    "existing": hit,
                }

        borderline_hits = [
            hit for hit in candidates
            if judge_threshold <= hit.get("score", 0.0) < high_threshold
        ]

        for hit in borderline_hits:
            is_duplicate = await self._judge_semantic_duplicate(
                existing=hit["content"],
                candidate=content,
                category=category,
            )
            if is_duplicate:
                return {
                    "reason": "semantic_judged",
                    "score": hit.get("score", 0.0),
                    "existing": hit,
                }

        return None

    async def _judge_semantic_duplicate(
        self,
        existing: str,
        candidate: str,
        category: str,
    ) -> bool:
        """Use a small LLM judgment only for borderline semantic matches."""
        try:
            llm = self._get_llm()
            prompt = _render_prompt(
                _SEMANTIC_DUPLICATE_JUDGE_PROMPT,
                category=category,
                existing=existing,
                candidate=candidate,
            )
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            verdict = response.content.strip().upper()
            return verdict.startswith("SAME")
        except Exception as e:
            logger.warning(
                "Semantic duplicate judge failed",
                category=category,
                error=str(e),
            )
            return False

    # ── 1. Context retrieval (called before every agent response) ─────────────

    async def get_relevant_context(
        self,
        query: str,
        n_knowledge: int = 4,
        n_conversations: int = 2,
    ) -> str:
        """
        Build a context string from relevant memories.
        This string gets injected into the agent's system prompt
        so Nura always knows what's relevant about Nitish.

        Returns a formatted string — empty sections are skipped.
        """
        if not chroma_store.is_ready:
            return "Memory not initialised yet."

        try:
            # Rewrite the query for better semantic retrieval
            search_query = await self._rewrite_query(query)

            knowledge_hits = await chroma_store.search_knowledge(
                search_query, n_results=n_knowledge
            )
            conv_hits = await chroma_store.search_conversations(
                search_query, n_results=n_conversations
            )

            parts = []

            # Only surface high-confidence matches (score > 0.4)
            good_knowledge = [h for h in knowledge_hits if h["score"] > 0.4]
            good_convs = [h for h in conv_hits if h["score"] > 0.4]

            if good_knowledge:
                parts.append("WHAT I KNOW ABOUT YOU:")
                for hit in good_knowledge:
                    category = hit["metadata"].get("category", "general")
                    parts.append(f"  [{category}] {hit['content']}")

            if good_convs:
                parts.append("\nPAST CONVERSATIONS:")
                for hit in good_convs:
                    date = hit["metadata"].get("created_at", "")[:10]
                    parts.append(f"  [{date}] {hit['content']}")

            if not parts:
                return "No relevant memories for this topic yet."

            return "\n".join(parts)

        except Exception as e:
            logger.warning("Context retrieval failed", error=str(e))
            return "Memory lookup unavailable."

    # ── 2. Auto-extraction after each conversation turn ───────────────────────

    async def extract_and_store(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
    ):
        """
        Extract learnings from a conversation turn and store them.

        Called as a background task after every response — does NOT
        block the user from getting their reply.
        """
        try:
            # Ask LLM to extract structured knowledge
            prompt = _render_prompt(
                KNOWLEDGE_EXTRACT_PROMPT,
                user_message=user_message,
                assistant_response=assistant_response,
            )
            llm = self._get_llm()
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            raw = response.content.strip()

            # Robust JSON extraction — handles extra text, fences, partial output
            extracted = _extract_json(raw)
            if extracted is None:
                logger.debug("No valid JSON in extraction response, skipping")
                return
            summary = extracted.get("summary", "")

            # Nothing worth storing
            if not summary or summary.lower() == "routine":
                logger.debug("Nothing to extract from this turn")
                return

            # Store conversation summary in ChromaDB for semantic recall
            await chroma_store.add_conversation_summary(
                session_id=session_id,
                summary=summary,
            )

            # Store each extracted item individually
            category_fields = {
                "facts":       "fact",
                "preferences": "preference",
                "decisions":   "decision",
                "goals":       "goal",
                "projects":    "project",
                "people":      "person",
            }

            for field, category in category_fields.items():
                items = extracted.get(field, [])
                for item in items:
                    if not item or len(item.strip()) < 10:
                        continue

                    duplicate = await self.find_duplicate_knowledge(
                        content=item,
                        category=category,
                    )
                    if duplicate:
                        logger.debug(
                            "Skipping duplicate extracted knowledge",
                            session=session_id[:8],
                            category=category,
                            reason=duplicate["reason"],
                            score=duplicate["score"],
                            preview=item[:80],
                        )
                        continue

                    # Store in ChromaDB (semantic search)
                    chroma_id = await chroma_store.add_knowledge(
                        content=item,
                        metadata={
                            "category": category,
                            "session_id": session_id,
                        },
                    )
                    # Store in MongoDB (structured browsing + filtering)
                    await mongo_store.save_knowledge(
                        content=item,
                        category=category,
                        source_session=session_id,
                        chroma_id=chroma_id,
                    )

            logger.debug(
                "Knowledge extracted and stored",
                session=session_id[:8],
                summary=summary[:80],
            )

        except json.JSONDecodeError:
            logger.warning("Knowledge extraction: LLM returned invalid JSON")
        except Exception as e:
            logger.warning("Knowledge extraction failed", error=str(e))

    # ── 3. Explicit knowledge storage ("remember that...") ───────────────────

    async def store_explicit(
        self,
        content: str,
        category: str = "fact",
        tags: list[str] | None = None,
        session_id: str | None = None,
    ) -> str:
        """
        Store something the user explicitly asked Nura to remember.
        Returns the ChromaDB ID of the stored entry.
        """
        duplicate = await self.find_duplicate_knowledge(content=content, category=category)
        if duplicate:
            logger.info(
                "Explicit knowledge already exists",
                category=category,
                reason=duplicate["reason"],
                score=duplicate["score"],
                preview=content[:60],
            )
            existing = duplicate.get("existing", {})
            return existing.get("chroma_id", "")

        chroma_id = await chroma_store.add_knowledge(
            content=content,
            metadata={
                "category": category,
                "explicit": True,
            },
        )
        await mongo_store.save_knowledge(
            content=content,
            category=category,
            tags=tags or [],
            source_session=session_id,
            chroma_id=chroma_id,
            metadata={"explicit": True},
        )
        logger.info(
            "Explicit knowledge stored",
            category=category,
            preview=content[:60],
        )
        return chroma_id

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _rewrite_query(self, message: str) -> str:
        """
        Rewrite the user's message as a short search query.
        Better search query → more relevant memories retrieved.
        Falls back to original message if LLM call fails.
        """
        try:
            llm = self._get_llm()
            prompt = KNOWLEDGE_QUERY_REWRITE_PROMPT.format(message=message)
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            rewritten = _sanitize_rewritten_query(response.content, message)
            logger.debug("Query rewritten", original=message[:50], rewritten=rewritten)
            return rewritten
        except Exception:
            return message  # safe fallback


# Singleton — import this everywhere
knowledge_service = KnowledgeService()
