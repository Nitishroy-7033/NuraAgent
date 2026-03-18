import logging
import os
import sys
from pathlib import Path
from core.config import config


def setup_logger(name: str):
    """
    Configures a logger with both console and file handlers.
    Usage: logger = setup_logger(__name__)
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if setup multiple times
    if logger.hasHandlers():
        return logger

    # Ensure log level is correctly parsed
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Define common format
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    log_path = Path(config.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(config.log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
