from typing import Generator
from .base_agent import BaseAgent
from core.chat import stream_chat, chat


CHAT_AGENT_PROMPT = """You are JARVIS, a highly intelligent personal AI assistant.
You are helpful, precise, and adaptive. You assist with coding, logic, research,
planning, and general knowledge. You remember context within a conversation.
Keep responses clear and structured."""


class ChatAgent(BaseAgent):
    """
    Basic conversational agent.
    Right now it wraps the chat function — later it can be extended
    with tools, memory retrieval, and decision making.
    """

    def __init__(self):
        super().__init__(
            name="ChatAgent",
            system_prompt=CHAT_AGENT_PROMPT,
        )

    def run(self, user_input: str) -> Generator[str, None, None]:
        """Streams response for the given user input."""
        return stream_chat(user_input, self.session)

    def run_sync(self, user_input: str) -> str:
        """Non-streaming version, returns full response string."""
        return chat(user_input, self.session)