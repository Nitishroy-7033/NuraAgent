from utils.prompts import NURA_SYSTEM_PROMPT
import httpx
import json
from typing import AsyncGenerator, List, Dict, Optional
from core.config import config as default_config
from utils.logger import Logger

default_logger = Logger("chat_service")

class ChatService:
    def __init__(self, config=None, logger=None):
        self.config = config or default_config
        self.logger = logger or default_logger

    async def stream_chat_completion(
        self, 
        query: str, 
        thread_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Asynchronously streams chat completions from the Ollama API using httpx.
        """
        self.logger.info(f"Query sending to Ollama API: {query}")
        
        messages = [
            {"role": "system", "content": NURA_SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]

        payload = {
            "model": self.config.ollama_model,
            "messages": messages,
            "stream": True
        }

        if not self.config.ollama_base_url:
            self.logger.error("Ollama base URL is not configured.")
            yield "JARVIS backend error: Ollama base URL is not configured."
            return

        url = f"{self.config.ollama_base_url}/api/chat"
        self.logger.debug(f"Ollama request URL: {url} | model: {self.config.ollama_model}")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    full_response = ""
                    
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                            
                        try:
                            chunk = json.loads(line)
                            token = chunk.get("message", {}).get("content", "")
                            
                            if token:
                                full_response += token
                                yield token
                                
                            if chunk.get("done"):
                                self.logger.info(f"Full response received: {full_response}")
                                if thread_id:
                                    self._add_to_memory(thread_id, query, full_response)
                                break
                        except json.JSONDecodeError as e:
                            self.logger.error(f"Error decoding JSON chunk: {e}")
                            continue

        except httpx.RequestError as e:
            self.logger.error(f"Network error communicating with Ollama API: {e}")
            yield "Check if Ollama is running at the configured URL."
        except FileNotFoundError as e:
            self.logger.error(
                f"Ollama connection failed (file not found): {type(e).__name__} - {e}"
            )
            yield "JARVIS backend error: Ollama endpoint not reachable."
        except OSError as e:
            self.logger.error(
                f"Ollama connection OS error: {type(e).__name__} - {e}"
            )
            yield "JARVIS backend error: Ollama connection failed."
        except Exception as e:
            self.logger.exception(
                f"Unexpected error in stream_chat_completion: {type(e).__name__} - {e}"
            )
            yield "An unexpected error occurred. Please try again later."

    async def chat_completion(
        self, 
        query: str, 
        thread_id: Optional[str] = None
    ) -> str:
        response_text = ""
        async for token in self.stream_chat_completion(
            query,
            thread_id=thread_id,
        ):
            # Simplistic error check for the UI
            if "running at" in token or "unexpected error" in token:
                if not response_text:
                    return token
            response_text += token
        return response_text

    def _add_to_memory(self, thread_id: str, query: str, response: str):
        """
        Placeholder for memory/history management.
        """
        self.logger.debug(f"Adding interaction to memory for thread: {thread_id}")
        # Add your persistent storage logic here
        pass
