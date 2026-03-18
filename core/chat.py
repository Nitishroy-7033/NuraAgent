import requests
import json
from typing import Generator, Optional
from core.config import config
from utils.logger import setup_logger

logger = setup_logger("core.chat")


SYSTEM_PROMPT = """You are JARVIS, a highly intelligent personal AI assistant.
You are helpful, precise, and adaptive. You assist with coding, logic, research, 
planning, and general knowledge. You remember context within a conversation.
Keep responses clear and structured."""


class ChatSession:
    """
    Manages a single conversation session with message history.
    Designed to be reusable inside an agent later.
    """

    def __init__(self, system_prompt: Optional[str] = None):
        self.system_prompt = system_prompt or SYSTEM_PROMPT
        self.history: list[dict] = []

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        # Trim history to avoid context overflow
        if len(self.history) > config.max_history:
            self.history = self.history[-config.max_history:]

    def get_messages(self) -> list[dict]:
        return self.history

    def clear(self):
        self.history = []


def stream_chat(
    user_input: str,
    session: ChatSession,
) -> Generator[str, None, None]:
    """
    Sends user message to Ollama and yields streamed response chunks.
    
    Args:
        user_input: The user's message
        session: ChatSession object holding history
        
    Yields:
        str: Each chunk of the response as it streams
    """

    # Add user message to history
    session.add_message("user", user_input)

    logger.debug(f"Sending request to Ollama ({config.ollama_model}): {user_input}")

    payload = {
        "model": config.ollama_model,
        "messages": [
            {"role": "system", "content": session.system_prompt},
            *session.get_messages(),
        ],
        "stream": True,
    }

    try:
        with requests.post(
            f"{config.ollama_base_url}/api/chat",
            json=payload,
            stream=True,
            timeout=120,
        ) as response:
            response.raise_for_status()

            full_response = ""

            for line in response.iter_lines():
                if not line:
                    continue

                chunk = json.loads(line.decode("utf-8"))
                token = chunk.get("message", {}).get("content", "")

                if token:
                    full_response += token
                    yield token

                # Ollama sends done=True on last chunk
                if chunk.get("done"):
                    break

            # Save full response to history
            session.add_message("assistant", full_response)

    except requests.exceptions.ConnectionError:
        error_msg = "[ERROR] Cannot connect to Ollama. Make sure it's running: `ollama serve`"
        logger.error(error_msg)
        yield f"\n{error_msg}"
    except requests.exceptions.Timeout:
        error_msg = "[ERROR] Request timed out. Try a shorter prompt."
        logger.error(error_msg)
        yield f"\n{error_msg}"
    except Exception as e:
        error_msg = f"[ERROR] Unexpected error: {str(e)}"
        logger.error(error_msg)
        yield f"\n{error_msg}"


def chat(user_input: str, session: ChatSession) -> str:
    """
    Non-streaming version. Collects full response and returns it.
    Useful for agents that need the complete response before acting.
    """
    return "".join(stream_chat(user_input, session))