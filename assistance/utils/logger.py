import logging
import sys
import structlog
from pathlib import Path

Path("./logs").mkdir(parents=True, exist_ok=True)


def setup_logging(log_level: str = "INFO", env: str = "development") -> None:
    level = getattr(logging, log_level.upper(), logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            structlog.dev.ConsoleRenderer(colors=True)
            if env == "development"
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
    )

    logging.basicConfig(
        level=level,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("./logs/nura.log"),
        ],
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    # Silence noisy libraries
    for noisy in ["httpx", "chromadb", "urllib3", "asyncio"]:
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str = "nura"):
    return structlog.get_logger(name)


# Run on import
try:
    from core.config import settings
    setup_logging(settings.nura.log_level, settings.nura.env)
except Exception:
    setup_logging()  # fallback with defaults