"""
intent_classifier.py — Routes every user message to the right agent

Strategy:
  1. Fast keyword shortcuts  → no LLM call, covers ~90% of cases
  2. Fallback to "chat"      → safe default, never crashes

NOTE: LLM-based classification is disabled — it causes OOM errors
when a large model (deepseek) is already loaded in Ollama's memory.
Keyword shortcuts are comprehensive enough for Phase 2.
"""
import re
from langchain_core.messages import BaseMessage

from utils.logger import get_logger

logger = get_logger("intent_classifier")

VALID_INTENTS = {
    "chat", "reasoning", "realtime",
    "entertainment", "system", "knowledge", "mcp",
}
DEFAULT_INTENT = "chat"


class IntentClassifier:

    async def classify(
        self,
        message: str,
        history: list[BaseMessage] | None = None,
    ) -> str:
        """Returns one of VALID_INTENTS. Never raises."""
        intent = self._keyword_shortcut(message) or DEFAULT_INTENT
        logger.debug(f"Intent: {intent} | msg: {message[:50]}")
        return intent

    def _keyword_shortcut(self, message: str) -> str | None:
        msg = message.lower().strip()

        # ── Knowledge ────────────────────────────────────────────────────────
        knowledge_triggers = [
            "remember that", "याद रखो", "याद रख",
            "store this", "note that", "save this",
            "remember:", "note:", "remember -",
        ]
        if any(msg.startswith(t) or t in msg for t in knowledge_triggers):
            return "knowledge"

        # ── Reasoning: math expressions ───────────────────────────────────────
        # Catches: "what is 5*5", "calculate sqrt(9)", "25 * 48 + 100"
        math_triggers = [
            "calculate", "calculate ", "compute", "solve",
            "what is ", "what's ", "sqrt", "factorial",
            "log(", "sin(", "cos(", "how much is",
        ]
        # Bare math expression: digits + operators
        has_math_expr = bool(re.search(r'\d+\s*[\+\-\*\/\^]\s*\d+', msg))
        if has_math_expr or any(t in msg for t in math_triggers):
            # But only if it looks like math, not a general "what is X" question
            if has_math_expr or any(t in msg for t in [
                "calculate", "compute", "sqrt", "factorial",
                "log(", "sin(", "cos(",
            ]):
                return "reasoning"

        # ── Reasoning: code ───────────────────────────────────────────────────
        code_triggers = [
            "write a function", "write a script", "write a program",
            "write code", "create a function", "create a script",
            "def ", "class ", "```", "import ",
            "debug ", "fix this code", "fix the bug",
            "algorithm", "implement ", "code to ",
            "python to ", "script to ",
        ]
        if any(t in msg for t in code_triggers):
            return "reasoning"

        # ── System ────────────────────────────────────────────────────────────
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
            "ek joke", "sunao", "hansi",
        ]
        if any(t in msg for t in entertainment_triggers):
            return "entertainment"

        # ── Realtime ──────────────────────────────────────────────────────────
        realtime_starts = ["news", "weather", "aaj ka", "today's", "latest "]
        realtime_contains = ["trending", "right now", "live update", "breaking news"]
        if any(msg.startswith(t) for t in realtime_starts):
            return "realtime"
        if any(t in msg for t in realtime_contains):
            return "realtime"

        # ── MCP ───────────────────────────────────────────────────────────────
        mcp_triggers = [
            "send email", "check email", "send whatsapp",
            "add to calendar", "create event", "check calendar",
            "create notion", "open notion",
        ]
        if any(t in msg for t in mcp_triggers):
            return "mcp"

        return None


# Singleton
intent_classifier = IntentClassifier()