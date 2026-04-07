import logging
import sys
from pathlib import Path

LOG_FILE = "logs/nura.log"


class StructuredLogger:
    """
    Thin wrapper over stdlib logging that supports structlog-style kwargs.
    Example: logger.info("Intent", session="abcd", value="chat")
    """

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def _format(self, msg: str, **kwargs) -> str:
        if not kwargs:
            return msg
        extras = " ".join(f"{k}={value!r}" for k, value in kwargs.items())
        return f"{msg} | {extras}"

    def debug(self, msg: str, *args, **kwargs):
        self._logger.debug(self._format(msg, **kwargs), *args)

    def info(self, msg: str, *args, **kwargs):
        self._logger.info(self._format(msg, **kwargs), *args)

    def warning(self, msg: str, *args, **kwargs):
        self._logger.warning(self._format(msg, **kwargs), *args)

    def error(self, msg: str, *args, **kwargs):
        self._logger.error(self._format(msg, **kwargs), *args)

    def exception(self, msg: str, *args, **kwargs):
        self._logger.exception(self._format(msg, **kwargs), *args)

    def __getattr__(self, name: str):
        return getattr(self._logger, name)


def setup_logger(name: str) -> StructuredLogger:
    """
    Configures a logger with both console and file handlers.
    Works with both old style Logger("name") and new get_logger("name").
    """
    from core.config import config  # local import to avoid circular

    logger = logging.getLogger(name)

    # Avoid duplicate handlers if called multiple times
    if not logger.hasHandlers():
        log_level = getattr(logging, config.log_level.upper(), logging.INFO)
        logger.setLevel(log_level)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler — always logs/nura.log
        log_path = Path(LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Quiet noisy libraries
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("chromadb").setLevel(logging.WARNING)
        logging.getLogger("motor").setLevel(logging.WARNING)

    return StructuredLogger(logger)


# Both aliases work
Logger = setup_logger
get_logger = setup_logger
