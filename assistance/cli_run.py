#!/usr/bin/env python3
"""
cli_run.py — Start Nura in CLI mode

Usage:
  python cli_run.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cli.chat_handler import run_cli

if __name__ == "__main__":
    try:
        asyncio.run(run_cli())
    except SystemExit:
        pass
    except KeyboardInterrupt:
        print("\nBye! 👋")