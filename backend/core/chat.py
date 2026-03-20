import requests
import json
from typing import Generator
from core.config import config
from utils.logger import setup_logger
from knowledge.store import ChatSession

logger = setup_logger("core.chat")




def stream_chat(
    user_input: str,
    session: ChatSession,
) -> Generator[str, None, None]:
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
                if chunk.get("done"):
                    break
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
    return "".join(stream_chat(user_input, session))