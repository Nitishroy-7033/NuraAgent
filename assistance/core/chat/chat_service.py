import requests
import json
from typing import Generator, List, Dict, Optional
from core.config import config as default_config
from utils.logger import Logger

default_logger = Logger("chat_service")

class ChatService:
    def __init__(self, config=None, logger=None):
        self.config = config or default_config
        self.logger = logger or default_logger

    def stream_chat_completion(
        self, 
        query: str, 
        system_prompt: Optional[str] = None, 
        thread_id: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Streams chat completions from the Ollama API.
        """
        self.logger.info(f"Query sending to Ollama API: {query}")
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt or "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]

        # Payload construction
        payload = {
            "model": self.config.ollama_model,
            "messages": messages,
            "stream": True
        }

        url = f"{self.config.ollama_base_url}/api/chat"

        try:
            with requests.post(
                url,
                json=payload,
                stream=True,
                timeout=120
            ) as response:
                response.raise_for_status()
                full_response = ""
                
                for line in response.iter_lines():
                    if not line:
                        continue
                        
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        token = chunk.get("message", {}).get("content", "")
                        
                        if token:
                            full_response += token
                            yield token
                            
                        if chunk.get("done"):
                            self.logger.info(f"Full response received: {full_response}")
                            # TODO: Add to memory/history logic here if thread_id is provided
                            if thread_id:
                                self._add_to_memory(thread_id, query, full_response)
                            break
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Error decoding JSON chunk: {e}")
                        continue

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error communicating with Ollama API: {e}")
            yield "Sorry, I'm having trouble connecting to the Ollama server."
        except Exception as e:
            self.logger.error(f"Unexpected error in stream_chat_completion: {e}")
            yield "An unexpected error occurred. Please try again later."

    def chat_completion(
        self, 
        query: str, 
        system_prompt: Optional[str] = None, 
        thread_id: Optional[str] = None
    ) -> str:
        """
        Returns a single string with the full chat completion.
        """
        response_text = ""
        for token in self.stream_chat_completion(query, system_prompt, thread_id):
            # Avoid accumulating error messages into the final response if possible
            if "trouble connecting" in token or "unexpected error" in token:
                # If we've already got some response, ignore the error token
                if response_text: continue
                return token
            response_text += token
        return response_text

    def _add_to_memory(self, thread_id: str, query: str, response: str):
        """
        Placeholder for memory/history management.
        """
        self.logger.debug(f"Adding interaction to memory for thread: {thread_id}")
        # Implementation will depend on how history is stored (e.g., redis, sqlite, memory)
        pass