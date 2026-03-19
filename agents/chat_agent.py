from typing import Generator
from .base_agent import BaseAgent
from core.chat import stream_chat, chat


from utils.prompts import JARVIS_SYSTEM_PROMPT

CHAT_AGENT_PROMPT = JARVIS_SYSTEM_PROMPT


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
        yield from stream_chat(user_input, self.session)

    def run_sync(self, user_input: str) -> str:
        """Non-streaming version, returns full response string."""
        return chat(user_input, self.session)

        