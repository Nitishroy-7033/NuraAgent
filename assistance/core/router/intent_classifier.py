"""
intent_classifier.py — Routes every user message to the right agent

Strategy:
  1. Fast keyword shortcuts  → no LLM call needed for obvious cases
  2. LLM classification      → for everything else
  3. Fallback to "chat"      → if anything fails
"""
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_ollama import ChatOllama

from core.config import config
from utils.logger import get_logger
from utils.prompts import INTENT_CLASSIFIER_PROMPT

logger = get_logger("intent_classifier")

# Must match the agent node names in orchestrator.py
VALID_INTENTS = {
    "chat",
    "reasoning",
    "realtime",
    "entertainment",
    "system",
    "knowledge",
    "mcp",
}

DEFAULT_INTENT = "chat"


class IntentClassifier:

    def __init__(self):
        self._llm: ChatOllama | None = None

    def _get_llm(self) -> ChatOllama:
        if self._llm is None:
            self._llm = ChatOllama(
                base_url=config.ollama.base_url,
                model=config.ollama.chat_model,
                temperature=0.0,   # fully deterministic — we want consistent routing
                num_predict=5,     # we only need one word back
            )
        return self._llm

    async def classify(
        self,
        message: str,
        history: list[BaseMessage] | None = None,
    ) -> str:
        """
        Classify a message and return one of the VALID_INTENTS.
        Always returns a string — never raises.
        """
        # Step 1: try fast keyword shortcut first (no LLM call)
        shortcut = self._keyword_shortcut(message)
        if shortcut:
            logger.debug("Intent via keyword shortcut", intent=shortcut)
            return shortcut

        # Step 2: LLM classification
        history_str = ""
        if history:
            last_six = history[-6:]   # last 3 pairs
            history_str = "\n".join(
                f"{m.type}: {m.content[:100]}" for m in last_six
            )

        prompt = INTENT_CLASSIFIER_PROMPT.format(
            message=message,
            history=history_str or "No prior history.",
        )

        try:
            llm = self._get_llm()
            response = await llm.ainvoke([HumanMessage(content=prompt)])

            # Extract just the first word, strip punctuation
            raw = response.content.strip().lower().split()[0]
            intent = "".join(c for c in raw if c.isalpha())

            if intent not in VALID_INTENTS:
                logger.warning(
                    "Unknown intent, falling back to default",
                    raw=raw,
                    fallback=DEFAULT_INTENT,
                )
                return DEFAULT_INTENT

            logger.debug("Intent via LLM", intent=intent, message=message[:50])
            return intent

        except Exception as e:
            logger.warning("Intent classification failed, using default", error=str(e))
            return DEFAULT_INTENT

    def _keyword_shortcut(self, message: str) -> str | None:
        """
        Rule-based shortcuts to skip the LLM call for obvious intents.
        Checks both starts-with and contains patterns.
        """
        msg = message.lower().strip()

        # ── Knowledge: explicit store commands ────────────────────────────────
        knowledge_triggers = [
            "remember that", "याद रखो", "याद रख",
            "store this", "note that", "save this",
            "remember:", "note:", "remember -",
        ]
        if any(msg.startswith(t) or t in msg for t in knowledge_triggers):
            return "knowledge"

        # ── System: OS / file commands ────────────────────────────────────────
        system_starts = ["open ", "close ", "launch ", "run ", "execute "]
        system_contains = [
            "find file", "search file", "create folder", "delete file",
            "take screenshot", "screenshot", "show desktop",
        ]
        if any(msg.startswith(t) for t in system_starts):
            return "system"
        if any(t in msg for t in system_contains):
            return "system"

        # ── Entertainment ─────────────────────────────────────────────────────
        entertainment_triggers = [
            "joke", "shayari", "शायरी", "mazak", "funny",
            "play game", "tell me a story", "riddle", "hasao",
        ]
        if any(t in msg for t in entertainment_triggers):
            return "entertainment"

        # ── Realtime: news / weather ──────────────────────────────────────────
        realtime_starts = ["news", "weather", "aaj ka", "today's", "latest "]
        realtime_contains = ["trending", "right now", "live update", "breaking"]
        if any(msg.startswith(t) for t in realtime_starts):
            return "realtime"
        if any(t in msg for t in realtime_contains):
            return "realtime"

        # ── Reasoning: code / math ────────────────────────────────────────────
        reasoning_triggers = [
            "```", "def ", "class ", "import ",
            "calculate ", "solve ", "debug ", "algorithm",
            "explain the math", "write code", "write a function",
        ]
        if any(t in msg for t in reasoning_triggers):
            return "reasoning"

        # ── MCP: integration actions ──────────────────────────────────────────
        mcp_triggers = [
            "send email", "check email", "send whatsapp",
            "add to calendar", "create event", "check calendar",
            "create notion", "open notion",
        ]
        if any(t in msg for t in mcp_triggers):
            return "mcp"

        return None  # no shortcut — let LLM decide


# Singleton
intent_classifier = IntentClassifier()