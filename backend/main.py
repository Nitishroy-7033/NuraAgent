import sys
import uvicorn
from agents.chat_agent import ChatAgent
from core.config import config
from utils.logger import setup_logger

logger = setup_logger("app")


def start_cli():
    logger.info(f"Starting {config.app_name} CLI...")
    print(f"\n{'='*50}")
    print(f"  {config.app_name} - Personal AI Assistant")
    print(f"  Model: {config.ollama_model}")
    print(f"  Type 'exit' to quit | 'clear' to reset chat")
    print(f"{'='*50}\n")

    agent = ChatAgent()

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                logger.info("User requested exit.")
                print("JARVIS: Goodbye.")
                break

            if user_input.lower() == "clear":
                agent.reset()
                logger.info("Chat history cleared.")
                print("JARVIS: Memory cleared.\n")
                continue

            print("JARVIS: ", end="", flush=True)

            for chunk in agent.run(user_input):
                print(chunk, end="", flush=True)

            print("\n")

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received.")
            print("\n\nJARVIS: Shutting down.")
            break


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        logger.info("Starting API server...")
        uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)
    else:
        start_cli()


if __name__ == "__main__":
    main()