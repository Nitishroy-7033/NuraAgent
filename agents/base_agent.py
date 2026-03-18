from abc import ABC, abstractmethod
from core.chat import ChatSession
from utils.logger import setup_logger


class BaseAgent(ABC):
    """
    Base class for all JARVIS agents.
    Every agent gets a ChatSession and must implement `run()`.
    """

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.logger = setup_logger(f"agents.{name.lower()}")
        self.session = ChatSession(system_prompt=system_prompt)
        self.logger.info(f"Agent '{self.name}' initialized.")

    @abstractmethod
    def run(self, user_input: str):
        """Each agent implements its own logic here."""
        pass

    def reset(self):
        self.session.clear()