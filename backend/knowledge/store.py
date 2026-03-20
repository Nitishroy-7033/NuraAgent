class ChatSession:
    def __init__(self, system_prompt: str):
        from utils.logger import setup_logger
        self.logger = setup_logger("knowledge.store")
        self.system_prompt = system_prompt
        self.history: list[dict] = []
        self.logger.debug(f"ChatSession initialized with {len(system_prompt)} chars of system prompt.")
    def add_message(self, role: str, content: str):
        from core.config import config
        self.history.append({"role": role, "content": content})
        self.logger.info(f"💾 Message stored: role={role}, length={len(content)}")
        if len(self.history) > config.max_history:
            self.history = self.history[-config.max_history:]
            self.logger.debug(f"✂️ History trimmed to {config.max_history} messages.")

    def get_messages(self) -> list[dict]:
        return self.history

    def clear(self):
        self.history = []
        if hasattr(self, 'logger'):
            self.logger.info("🗑️ ChatSession memory cleared.")
