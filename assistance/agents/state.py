"""
state.py — Shared state for the Nura LangGraph

This single object flows through every node in the graph.
Each node reads from it and returns a partial dict to update it.

The `messages` field uses LangGraph's add_messages reducer —
messages are APPENDED, not replaced, on every update.
"""
from typing import Annotated, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class NuraState(BaseModel):

    # ── Conversation ──────────────────────────────────────────────────────────
    # add_messages reducer: new messages are appended to the list
    messages: Annotated[list[BaseMessage], add_messages] = Field(default_factory=list)

    # ── Routing ───────────────────────────────────────────────────────────────
    intent: str = "chat"            # set by intent_router node
    active_agent: str = "chat_agent"

    # ── Session ───────────────────────────────────────────────────────────────
    session_id: str = ""
    user_id: str = ""
    user_message: str = ""          # raw latest message — easy access for all nodes

    # ── Memory ────────────────────────────────────────────────────────────────
    knowledge_context: str = ""     # fetched by context_loader, injected into prompts

    # ── Output ────────────────────────────────────────────────────────────────
    response: str = ""              # final text response surfaced to user
    error: str = ""                 # any error from an agent

    # ── Metadata ─────────────────────────────────────────────────────────────
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True  # needed for BaseMessage