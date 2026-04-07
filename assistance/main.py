
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def start_api():
    import uvicorn
    from core.config import config
    uvicorn.run(
        "apis.api_controller:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.env == "development",
        log_level=config.log_level.lower(),
    )


def start_cli():
    import asyncio
    from cli.chat_handler import run_cli
    try:
        asyncio.run(run_cli())
    except SystemExit:
        pass
    except KeyboardInterrupt:
        print("\nBye! 👋")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "api"
    if mode == "cli":
        start_cli()
    else:
        start_api()