"""
orchestrator.py — Nura's LangGraph supervisor

Full flow:
  START
    → context_loader      fetch relevant memories from knowledge base
    → intent_router       classify message → pick agent
    → [agent node]        chat | reasoning | entertainment | realtime | system | knowledge | mcp
    → knowledge_writer    save message + background knowledge extraction
    → END

Public API:
  nura = NuraOrchestrator()
  await nura.init()
  result = await nura.chat(message, session_id)
  async for chunk in nura.stream(message, session_id): ...
"""
import asyncio
import uuid
from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

from agents.state import NuraState
from core.config import config
from core.knowledge.knowledge_service import knowledge_service
from core.knowledge.mongo_store import mongo_store
from core.router.intent_classifier import intent_classifier
from utils.logger import get_logger
from utils.prompts import (
    CHAT_AGENT_PROMPT,
    REASONING_AGENT_PROMPT,
    NURA_IDENTITY,
)
from agents.reasoning_agent import build_reasoning_agent

logger = get_logger("orchestrator")

_INPUT_TOKEN_KEYS = (
    "input_tokens",
    "prompt_tokens",
    "prompt_token_count",
    "prompt_eval_count",
)
_OUTPUT_TOKEN_KEYS = (
    "output_tokens",
    "completion_tokens",
    "completion_token_count",
    "eval_count",
)


def _to_mapping(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        try:
            dumped = value.model_dump()
            if isinstance(dumped, dict):
                return dumped
        except Exception:
            pass
    if hasattr(value, "dict"):
        try:
            dumped = value.dict()
            if isinstance(dumped, dict):
                return dumped
        except Exception:
            pass
    return None


def _to_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return int(stripped)
        except ValueError:
            return None
    return None


def _first_present_int(mapping: dict[str, Any], keys: tuple[str, ...]) -> int | None:
    for key in keys:
        value = _to_int(mapping.get(key))
        if value is not None:
            return value
    return None


def _extract_tokens_from_payload(
    payload: Any,
    depth: int = 0,
) -> tuple[int | None, int | None]:
    if payload is None or depth > 3:
        return None, None

    mapping = _to_mapping(payload)
    if mapping is None:
        return None, None

    input_tokens = _first_present_int(mapping, _INPUT_TOKEN_KEYS)
    output_tokens = _first_present_int(mapping, _OUTPUT_TOKEN_KEYS)
    if input_tokens is not None or output_tokens is not None:
        return input_tokens, output_tokens

    for key in ("usage_metadata", "response_metadata", "generation_info", "message", "chunk", "output"):
        if key in mapping:
            found_input, found_output = _extract_tokens_from_payload(mapping.get(key), depth + 1)
            if found_input is not None or found_output is not None:
                return found_input, found_output

    generations = mapping.get("generations")
    if isinstance(generations, list):
        for item in generations:
            found_input, found_output = _extract_tokens_from_payload(item, depth + 1)
            if found_input is not None or found_output is not None:
                return found_input, found_output

    return None, None


def _extract_tokens_from_event(event: dict[str, Any]) -> tuple[int, int]:
    data = event.get("data", {})
    if isinstance(data, dict):
        candidates = (data, data.get("output"), data.get("chunk"))
    else:
        candidates = (data,)

    for candidate in candidates:
        input_tokens, output_tokens = _extract_tokens_from_payload(candidate)
        if input_tokens is not None or output_tokens is not None:
            return input_tokens or 0, output_tokens or 0
    return 0, 0


# ═════════════════════════════════════════════════════════════════════════════
# GRAPH NODES
# ═════════════════════════════════════════════════════════════════════════════

async def context_loader_node(state: NuraState) -> dict:
    """
    Pre-agent node — fetch relevant memories before any agent responds.
    Injects memory into the state so agents always know about Nitish.
    """
    if not state.user_message:
        return {}

    context = await knowledge_service.get_relevant_context(
        query=state.user_message,
        n_knowledge=4,
        n_conversations=2,
    )
    logger.debug("Context loaded", chars=len(context))
    return {"knowledge_context": context}


async def intent_router_node(state: NuraState) -> dict:
    """
    Classify the user message and set the routing intent.
    The conditional edge reads state.intent to pick the next node.
    """
    intent = await intent_classifier.classify(
        message=state.user_message,
        history=state.messages[:-1],    # exclude current message
    )
    logger.info("Intent", value=intent, session=state.session_id[:8])
    return {"intent": intent, "active_agent": f"{intent}_agent"}


def route_to_agent(
    state: NuraState,
) -> Literal[
    "chat_agent",
    "reasoning_agent",
    "entertainment_agent",
    "realtime_agent",
    "system_agent",
    "knowledge_agent",
    "mcp_agent",
]:
    """Conditional edge — maps intent → agent node name."""
    mapping = {
        "chat":          "chat_agent",
        "reasoning":     "reasoning_agent",
        "entertainment": "entertainment_agent",
        "realtime":      "realtime_agent",
        "system":        "system_agent",
        "knowledge":     "knowledge_agent",
        "mcp":           "mcp_agent",
    }
    return mapping.get(state.intent, "chat_agent")


async def knowledge_writer_node(state: NuraState) -> dict:
    """
    Post-agent node — save conversation + trigger background extraction.
    Never delays the user's response.
    """
    if not state.user_message or not state.response:
        return {}

    # Save both turns to MongoDB
    await mongo_store.save_message(
        session_id=state.session_id,
        role="user",
        content=state.user_message,
        metadata={"intent": state.intent},
    )
    await mongo_store.save_message(
        session_id=state.session_id,
        role="assistant",
        content=state.response,
        metadata={"agent": state.active_agent},
    )

    # Fire-and-forget: extract knowledge in background
    asyncio.create_task(
        knowledge_service.extract_and_store(
            session_id=state.session_id,
            user_message=state.user_message,
            assistant_response=state.response,
        )
    )
    return {}


# ═════════════════════════════════════════════════════════════════════════════
# AGENT NODE FACTORIES
# ═════════════════════════════════════════════════════════════════════════════

def _make_llm(model: str, temperature: float = 0.7) -> ChatOllama:
    return ChatOllama(
        base_url=config.ollama.base_url,
        model=model,
        temperature=temperature,
        num_ctx=config.ollama.num_ctx,
    )


def _build_chat_agent():
    llm = _make_llm(config.ollama.chat_model, temperature=0.7)

    async def node(state: NuraState) -> dict:
        logger.info("Chat agent", session=state.session_id[:8])
        system = CHAT_AGENT_PROMPT.format(
            knowledge_context=state.knowledge_context or "No prior memories."
        )
        messages = [SystemMessage(content=system)] + list(state.messages)
        try:
            resp = await llm.ainvoke(messages)
            return {
                "messages": [AIMessage(content=resp.content)],
                "response": resp.content,
                "active_agent": "chat_agent",
            }
        except Exception as e:
            err = f"Chat error: {e}"
            logger.error(err)
            return {"messages": [AIMessage(content=err)], "response": err, "error": str(e)}

    return node


def _build_reasoning_agent():
    # Falls back to chat model if reasoning model not available
    llm = _make_llm(config.ollama.reasoning_model, temperature=0.2)
    fallback_llm = _make_llm(config.ollama.chat_model, temperature=0.2)

    async def node(state: NuraState) -> dict:
        logger.info("Reasoning agent", session=state.session_id[:8])
        system = REASONING_AGENT_PROMPT.format(
            knowledge_context=state.knowledge_context or "No prior memories."
        )
        messages = [SystemMessage(content=system)] + list(state.messages)
        try:
            resp = await llm.ainvoke(messages)
        except Exception:
            logger.warning("Reasoning model unavailable, falling back to chat model")
            resp = await fallback_llm.ainvoke(messages)
        return {
            "messages": [AIMessage(content=resp.content)],
            "response": resp.content,
            "active_agent": "reasoning_agent",
        }

    return node


def _build_knowledge_agent():
    """Handles explicit 'remember that...' commands."""

    async def node(state: NuraState) -> dict:
        logger.info("Knowledge agent", session=state.session_id[:8])
        msg = state.user_message

        # Strip the trigger phrase to get the actual content
        content = msg
        for trigger in [
            "remember that", "store this", "note that",
            "save this", "याद रखो", "याद रख",
            "remember:", "note:", "remember -",
        ]:
            if content.lower().startswith(trigger):
                content = content[len(trigger):].strip(": ").strip()
                break

        if len(content) > 5:
            await knowledge_service.store_explicit(
                content=content,
                session_id=state.session_id,
            )
            reply = f"✓ Yaad kar liya:\n\n\"{content}\"\n\nTeri knowledge base mein save ho gaya."
        else:
            reply = "Kya yaad karna hai? Thoda aur detail mein batao."

        return {
            "messages": [AIMessage(content=reply)],
            "response": reply,
            "active_agent": "knowledge_agent",
        }

    return node


def _build_stub_agent(name: str):
    """
    Generic stub for agents not fully built yet (entertainment, realtime, system, mcp).
    Still uses the LLM — just no specialized tools yet.
    Phase 2 will replace these with full implementations.
    """
    llm = _make_llm(config.ollama.chat_model, temperature=0.7)

    async def node(state: NuraState) -> dict:
        logger.info(f"{name} (stub)", session=state.session_id[:8])
        system = f"{NURA_IDENTITY}\n\nAnswer the user's request as helpfully as you can."
        messages = [SystemMessage(content=system)] + list(state.messages)
        resp = await llm.ainvoke(messages)
        return {
            "messages": [AIMessage(content=resp.content)],
            "response": resp.content,
            "active_agent": name,
        }

    return node


# ═════════════════════════════════════════════════════════════════════════════
# GRAPH BUILDER
# ═════════════════════════════════════════════════════════════════════════════

def _build_graph():
    graph = StateGraph(NuraState)

    # Register all nodes
    graph.add_node("context_loader",      context_loader_node)
    graph.add_node("intent_router",       intent_router_node)
    graph.add_node("chat_agent",          _build_chat_agent())
    graph.add_node("reasoning_agent",     build_reasoning_agent())
    graph.add_node("knowledge_agent",     _build_knowledge_agent())
    graph.add_node("entertainment_agent", _build_stub_agent("entertainment_agent"))
    graph.add_node("realtime_agent",      _build_stub_agent("realtime_agent"))
    graph.add_node("system_agent",        _build_stub_agent("system_agent"))
    graph.add_node("mcp_agent",           _build_stub_agent("mcp_agent"))
    graph.add_node("knowledge_writer",    knowledge_writer_node)

    # Wire the flow
    graph.add_edge(START, "context_loader")
    graph.add_edge("context_loader", "intent_router")

    # intent_router → one of the agent nodes (conditional)
    all_agents = [
        "chat_agent", "reasoning_agent", "knowledge_agent",
        "entertainment_agent", "realtime_agent", "system_agent", "mcp_agent",
    ]
    graph.add_conditional_edges(
        "intent_router",
        route_to_agent,
        {agent: agent for agent in all_agents},
    )

    # Every agent → knowledge_writer → END
    for agent in all_agents:
        graph.add_edge(agent, "knowledge_writer")
    graph.add_edge("knowledge_writer", END)

    compiled = graph.compile()
    logger.info("LangGraph compiled successfully")
    return compiled


# ═════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═════════════════════════════════════════════════════════════════════════════

class NuraOrchestrator:
    """
    High-level wrapper around the compiled LangGraph.
    This is what the CLI and API call.
    """

    def __init__(self):
        self._graph = None

    async def init(self):
        """Init knowledge stores and compile the graph. Call once at startup."""
        await knowledge_service.init()
        self._graph = _build_graph()
        logger.info("NuraOrchestrator ready")

    def _check_ready(self):
        if not self._graph:
            raise RuntimeError("Call await nura.init() before using the orchestrator.")

    async def chat(
        self,
        message: str,
        session_id: str | None = None,
        history: list[dict] | None = None,
    ) -> dict:
        """
        Send a message and get a complete response.

        Returns:
          {
            "response":   str,
            "intent":     str,
            "agent":      str,
            "session_id": str,
            "error":      str,
          }
        """
        self._check_ready()
        session_id = session_id or str(uuid.uuid4())

        # Build message list from history + current message
        lc_messages = []
        if history:
            for turn in history:
                if turn.get("role") == "user":
                    lc_messages.append(HumanMessage(content=turn["content"]))
                elif turn.get("role") == "assistant":
                    lc_messages.append(AIMessage(content=turn["content"]))
        lc_messages.append(HumanMessage(content=message))

        initial_state = NuraState(
            messages=lc_messages,
            user_message=message,
            session_id=session_id,
            user_id=config.user_id,
        )

        result = await self._graph.ainvoke(initial_state)

        return {
            "response":   result.get("response", ""),
            "intent":     result.get("intent", "chat"),
            "agent":      result.get("active_agent", "chat_agent"),
            "session_id": session_id,
            "error":      result.get("error", ""),
        }

    async def stream(
        self,
        message: str,
        session_id: str | None = None,
    ):
        """
        Stream response chunks as they arrive.
        Used by the WebSocket and SSE API endpoints.

        Yields dicts:
          {"type": "chunk", "content": "...", "session_id": "..."}
          {"type": "done",  "intent": "...", "agent": "...", "session_id": "..."}
          {"type": "error", "content": "...", "session_id": "..."}
        """
        self._check_ready()
        session_id = session_id or str(uuid.uuid4())
        lc_messages = [HumanMessage(content=message)]
        total_input_tokens = 0
        total_output_tokens = 0
        routed_intent = "chat"
        routed_agent = "chat_agent"

        initial_state = NuraState(
            messages=lc_messages,
            user_message=message,
            session_id=session_id,
            user_id=config.user_id,
        )

        try:
            yield {
                "type": "start",
                "stage": "thinking",
                "content": "Loading context and selecting the best agent.",
                "session_id": session_id,
            }

            async for event in self._graph.astream_events(initial_state, version="v2"):
                kind = event.get("event", "")

                if kind == "on_chat_model_end":
                    input_tokens, output_tokens = _extract_tokens_from_event(event)
                    total_input_tokens += input_tokens
                    total_output_tokens += output_tokens
                    continue

                if kind == "on_chain_end" and event.get("name") == "intent_router":
                    output = event.get("data", {}).get("output", {})
                    routed_intent = output.get("intent", routed_intent)
                    routed_agent = output.get("active_agent", routed_agent)
                    yield {
                        "type": "thinking",
                        "stage": "routing",
                        "content": f"Intent='{routed_intent}' -> agent='{routed_agent}'.",
                        "intent": routed_intent,
                        "agent": routed_agent,
                        "session_id": session_id,
                    }
                    continue

                if kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        yield {
                            "type":       "chunk",
                            "content":    chunk.content,
                            "session_id": session_id,
                        }

                elif kind == "on_chain_end" and event.get("name") == "LangGraph":
                    output = event.get("data", {}).get("output", {})
                    yield {
                        "type":       "done",
                        "intent":     output.get("intent", routed_intent),
                        "agent":      output.get("active_agent", routed_agent),
                        "input_tokens": total_input_tokens,
                        "output_tokens": total_output_tokens,
                        "total_tokens": total_input_tokens + total_output_tokens,
                        "session_id": session_id,
                    }

        except Exception as e:
            logger.error("Stream error", error=str(e))
            yield {"type": "error", "content": str(e), "session_id": session_id}


# Global singleton — used by CLI and API
nura = NuraOrchestrator()
