from dataclasses import dataclass


@dataclass
class Config:
    # Ollama settings
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3:8b"  # change to your model

    # Chat settings
    max_history: int = 20  # max messages to keep in context
    stream: bool = True

    # App settings
    app_name: str = "JARVIS"
    debug: bool = True

    # Logging settings
    log_level: str = "DEBUG"
    log_file: str = "logs/app.log"


config = Config()