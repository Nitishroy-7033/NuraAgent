"""
reasoning_agent.py — Nura's Reasoning Agent

Uses deepseek-r1:8b for step-by-step thinking.

Flow for each message:
  1. Analyse the request — what kind of reasoning is needed?
  2. If code needed   → generate + execute Python, show result
  3. If math needed   → evaluate expression safely, show working
  4. If analysis only → structured step-by-step response
  5. Always clean up DeepSeek's <think>...</think> tags for display
"""
import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from agents.state import NuraState
from agents.tools.code_executor import execute_python, format_result as fmt_code
from agents.tools.math_tool import evaluate_math, format_result as fmt_math
from core.config import config
from utils.logger import get_logger

logger = get_logger("reasoning_agent")

# ── System prompt ─────────────────────────────────────────────────────────────

REASONING_SYSTEM = """You are Nura's Reasoning Agent — powered by DeepSeek-R1.
You are built for {user_name} and have deep knowledge of their context.

YOUR STRENGTHS:
- Step-by-step mathematical reasoning (show every step)
- Writing, debugging, and explaining code in any language
- Breaking down complex problems into clear sub-problems
- Research synthesis and structured analysis
- Decision making with pros/cons and clear recommendations

WHAT YOU KNOW ABOUT {user_name_upper}:
{knowledge_context}

RESPONSE FORMAT RULES:
- For math: show the formula, working, and final answer clearly
- For code: write clean, commented code. Explain what it does.
- For analysis: use Problem → Approach → Solution → Conclusion structure
- Be direct — give a real answer and recommendation, not "it depends"
- If writing code to solve something, mention that it was executed and show output

IMPORTANT: You have a code execution tool and a math tool available.
When the user asks you to calculate or run something, USE them — don't just show code, run it."""

# ── Intent detection within reasoning ────────────────────────────────────────

_CODE_PATTERNS = [
    r"```[\w]*\n",           # code block
    r"\bwrite\b.*\bcode\b",
    r"\bwrite\b.*\bscript\b",
    r"\bwrite\b.*\bfunction\b",
    r"\bwrite\b.*\bprogram\b",
    r"\bdebug\b",
    r"\bfix\b.*\b(bug|error|code)\b",
    r"\bimplement\b",
    r"\bdef \w+\(",
    r"\bclass \w+",
]

_MATH_PATTERNS = [
    r"\bcalculate\b",
    r"\bcompute\b",
    r"\bsolve\b",
    r"\beval(uate)?\b",
    r"\bwhat\s+is\s+[\d\s\+\-\*\/\^\(\)]+",
    r"[\d]+\s*[\+\-\*\/\^]\s*[\d]+",   # e.g. "25 * 48"
    r"\bsqrt\b|\blog\b|\bsin\b|\bcos\b",
]


def _needs_code(message: str) -> bool:
    msg = message.lower()
    return any(re.search(p, msg) for p in _CODE_PATTERNS)


def _needs_math(message: str) -> bool:
    msg = message.lower()
    return any(re.search(p, msg) for p in _MATH_PATTERNS)


def _clean_deepseek_output(text: str) -> str:
    """
    DeepSeek-R1 wraps its thinking in <think>...</think> tags.
    We strip those for the final response — the user gets clean output.
    (We could optionally show them as a collapsible section in the UI later.)
    """
    # Remove <think>...</think> blocks
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()


# ── Code extraction from LLM response ────────────────────────────────────────

def _extract_code_blocks(text: str) -> list[str]:
    """Pull all ```python ... ``` blocks out of the LLM's response."""
    blocks = re.findall(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return [b.strip() for b in blocks if b.strip()]


# ── Main agent node ───────────────────────────────────────────────────────────

def build_reasoning_agent():
    """Returns the LangGraph node function for the Reasoning Agent."""

    llm = ChatOllama(
        base_url=config.ollama.base_url,
        model=config.ollama.reasoning_model,   # deepseek-r1:8b
        temperature=0.2,                        # low = more deterministic reasoning
        num_ctx=config.ollama.num_ctx,
    )

    # Fallback to chat model if deepseek not available
    fallback_llm = ChatOllama(
        base_url=config.ollama.base_url,
        model=config.ollama.chat_model,
        temperature=0.2,
        num_ctx=config.ollama.num_ctx,
    )

    async def reasoning_node(state: NuraState) -> dict:
        logger.info("Reasoning agent activated", session=state.session_id[:8])

        user_message = state.user_message
        needs_code = _needs_code(user_message)
        needs_math = _needs_math(user_message)

        logger.debug(
            "Reasoning type detected",
            needs_code=needs_code,
            needs_math=needs_math,
        )

        # ── Step 1: Quick math shortcut (no LLM needed) ───────────────────────
        # For simple expressions like "what is 25 * 48 + 100"
        if needs_math and not needs_code:
            math_expr = _extract_math_expression(user_message)
            if math_expr:
                math_result = evaluate_math(math_expr)
                if math_result["success"]:
                    # Build a proper answer with working shown
                    quick_answer = (
                        f"**Calculation:** {fmt_math(math_result)}\n\n"
                        f"Let me also explain the working:"
                    )
                    # Now ask LLM to explain if needed, or just return quick answer
                    if len(user_message.split()) <= 10:
                        # Short question — just return the calc result
                        reply = f"**{math_result['expression']}**\n\n= **{math_result['result_str']}**"
                        return _make_result(state, reply)

        # ── Step 2: Get LLM response ──────────────────────────────────────────
        system = REASONING_SYSTEM.format(
            user_name=config.user_name,
            user_name_upper=config.user_name.upper(),
            knowledge_context=state.knowledge_context or "No prior context.",
        )
        messages_to_send = [SystemMessage(content=system)] + list(state.messages)

        try:
            resp = await llm.ainvoke(messages_to_send)
            raw_reply = resp.content
        except Exception as e:
            logger.warning("DeepSeek unavailable, falling back", error=str(e))
            try:
                resp = await fallback_llm.ainvoke(messages_to_send)
                raw_reply = resp.content
            except Exception as e2:
                err = f"Reasoning model error: {e2}"
                return _make_result(state, err, error=str(e2))

        # Clean DeepSeek's <think> tags
        reply = _clean_deepseek_output(raw_reply)

        # ── Step 3: Execute any code blocks LLM generated ────────────────────
        if needs_code:
            code_blocks = _extract_code_blocks(reply)
            if code_blocks:
                logger.info("Executing code from LLM", blocks=len(code_blocks))
                execution_results = []

                for code in code_blocks:
                    exec_result = await execute_python(code)
                    execution_results.append(exec_result)

                # Append execution results to the reply
                exec_section = "\n\n---\n**Execution Results:**\n"
                for i, result in enumerate(execution_results):
                    if len(code_blocks) > 1:
                        exec_section += f"\n*Block {i+1}:*\n"
                    if result["success"] and result["output"]:
                        exec_section += f"```\n{result['output']}\n```\n"
                    elif result["success"] and not result["output"]:
                        exec_section += "*(ran successfully, no output)*\n"
                    else:
                        exec_section += f"**Error:** `{result['error']}`\n"

                reply = reply + exec_section

        logger.debug("Reasoning complete", reply_len=len(reply))
        return _make_result(state, reply)

    return reasoning_node


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_result(state: NuraState, reply: str, error: str = "") -> dict:
    return {
        "messages": [AIMessage(content=reply)],
        "response": reply,
        "active_agent": "reasoning_agent",
        "error": error,
    }


def _extract_math_expression(message: str) -> str | None:
    """
    Try to extract a pure math expression from a message like
    'what is 25 * 48 + 100?' or 'calculate sqrt(144)'
    """
    # Strip common question prefixes
    prefixes = [
        "what is", "calculate", "compute", "solve", "eval",
        "evaluate", "what's", "whats",
    ]
    cleaned = message.lower().strip().rstrip("?").strip()
    for p in prefixes:
        if cleaned.startswith(p):
            cleaned = cleaned[len(p):].strip()
            break

    # Basic check: does it look like a math expression?
    allowed_chars = set("0123456789+-*/^().,%! sqrtlogsincotanabepiflorceil")
    if cleaned and all(c in allowed_chars or c.isspace() for c in cleaned):
        # Replace ^ with ** for Python
        cleaned = cleaned.replace("^", "**")
        return cleaned

    return None