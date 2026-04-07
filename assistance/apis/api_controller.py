from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.orchestrator import nura
from core.config import config
from core.knowledge.mongo_store import mongo_store
from utils.logger import LOG_FILE, get_logger

logger = get_logger("api")


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    bind_host = config.api_host
    display_host = "127.0.0.1" if bind_host in ("0.0.0.0", "::") else bind_host
    base_url = f"http://{display_host}:{config.api_port}"
    log_path = Path(LOG_FILE).resolve()

    logger.info(
        f"{config.app_name} API starting...",
        env=config.env,
        user=config.user_name,
    )
    logger.info("API bound", host=bind_host, port=config.api_port)
    logger.info(
        "API URLs",
        base=base_url,
        docs=f"{base_url}/docs",
        redoc=f"{base_url}/redoc",
        health=f"{base_url}/health",
    )
    logger.info(
        "Models",
        ollama_base_url=config.ollama.base_url,
        chat_model=config.ollama.chat_model,
        reasoning_model=config.ollama.reasoning_model,
        embed_model=config.ollama.embed_model,
    )
    logger.info("Logging to file", path=str(log_path))

    await nura.init()
    logger.info(f"{config.app_name} API ready")
    yield
    logger.info(f"{config.app_name} API shutting down...")
    await mongo_store.close()


from apis.routes import agent, sessions, knowledge, profile

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Nura API",
    description=f"Personal AI assistant for {config.user_name}",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "user": config.user_name,
        "model": config.ollama.chat_model,
    }


# ── Include Routers ───────────────────────────────────────────────────────────

app.include_router(agent.router)
app.include_router(sessions.router)
app.include_router(knowledge.router)
app.include_router(profile.router)
