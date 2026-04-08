from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OLLAMA_", extra="ignore")
    base_url: str = "http://localhost:11434"
    chat_model: str = "llama3:8b"  # Changed from llama3.1:8b to reduce memory usage
    reasoning_model: str = "deepseek-r1:8b"
    embed_model: str = "nomic-embed-text"
    knowledge_extractor_model: str = "llama3:8b"  # Use same model as chat for better JSON handling
    temperature: float = 0.7
    num_ctx: int = 4096  # Reduced from 8192 to save memory


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MONGO_", extra="ignore")
    uri: str = "mongodb://localhost:27017"
    db_name: str = "NuraAgent"
    collection_chat_history: str = "ChatHistory"
    collection_sessions: str = "Sessions"
    collection_knowledge: str = "KnowledgeBase"
    collection_users: str = "Users"


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_", extra="ignore")
    url: str = "redis://localhost:6379"


class ChromaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CHROMA_", extra="ignore")
    persist_dir: str = "./data/chroma"
    collection_knowledge: str = "nura_knowledge"
    collection_conversations: str = "nura_conversations"
    semantic_duplicate_high_threshold: float = 0.93
    semantic_duplicate_judge_threshold: float = 0.82
    semantic_duplicate_candidates: int = 5


class NuraSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NURA_", extra="ignore")
    user_id: str = "nitish"
    user_name: str = "Nitish"
    app_name: str = "JARVIS"
    log_level: str = "INFO"
    env: str = "development"


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="API_", extra="ignore")
    host: str = "0.0.0.0"
    port: int = 8000


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    mongo: MongoSettings = Field(default_factory=MongoSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    chroma: ChromaSettings = Field(default_factory=ChromaSettings)
    nura: NuraSettings = Field(default_factory=NuraSettings)
    api: APISettings = Field(default_factory=APISettings)

    def model_post_init(self, __context):
        Path(self.chroma.persist_dir).mkdir(parents=True, exist_ok=True)
        Path("./data/uploads").mkdir(parents=True, exist_ok=True)
        Path("./logs").mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


class ConfigProxy:
    """
    Backwards-compatible adapter for older modules that expect flat config fields.
    Prefer using `settings` for new code.
    """

    def __init__(self, cfg: Settings):
        self._cfg = cfg

    # Nested settings
    @property
    def ollama(self) -> OllamaSettings:
        return self._cfg.ollama

    @property
    def mongo(self) -> MongoSettings:
        return self._cfg.mongo

    @property
    def redis(self) -> RedisSettings:
        return self._cfg.redis

    @property
    def chroma(self) -> ChromaSettings:
        return self._cfg.chroma

    @property
    def api(self) -> APISettings:
        return self._cfg.api

    @property
    def nura(self) -> NuraSettings:
        return self._cfg.nura

    # Flat compatibility fields
    @property
    def ollama_base_url(self) -> str:
        return self._cfg.ollama.base_url

    @property
    def ollama_model(self) -> str:
        return self._cfg.ollama.chat_model

    @property
    def api_host(self) -> str:
        return self._cfg.api.host

    @property
    def api_port(self) -> int:
        return self._cfg.api.port

    @property
    def log_level(self) -> str:
        return self._cfg.nura.log_level

    @property
    def env(self) -> str:
        return self._cfg.nura.env

    @property
    def user_id(self) -> str:
        return self._cfg.nura.user_id

    @property
    def user_name(self) -> str:
        return self._cfg.nura.user_name

    @property
    def app_name(self) -> str:
        return self._cfg.nura.app_name

    def __getattr__(self, name: str):
        # Fallback to underlying Settings for any other attribute access
        return getattr(self._cfg, name)


# Backwards-compatible alias used across the codebase
config = ConfigProxy(settings)
