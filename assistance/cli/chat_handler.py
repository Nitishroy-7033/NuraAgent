import logging
import asyncio
from colorama import Fore, Style
from core.chat.chat_service import ChatService
from core.config import config
from cli.ui import print_header

def start_chat(streaming=True, thread_id="cli_session", system_prompt=None):
    """
    Synchronous bridge as CLI's main entry point, but runs the async chat loop inside.
    """
    try:
        asyncio.run(_async_chat_loop(streaming, thread_id, system_prompt))
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nExiting chat session...")

async def _async_chat_loop(streaming, thread_id, system_prompt):
    """
    Asynchronous chat loop handler.
    """
    chat_service = ChatService()
    
    # Silence logger info during interactive chat to keep it clean
    for logger_name in ["chat_service", "api_controller", "cli_run"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    print_header()
    mode = "Streaming" if streaming else "Static"
    print(Fore.YELLOW + f"{mode} mode activated. (Type 'menu' or 'exit' to go back)")
    print("-" * 50)

    while True:
        try:
            # input() is blocking but for local CLI it's generally acceptable.
            # Using loop.run_in_executor if we wanted it truly non-blocking here.
            user_input = input(Fore.GREEN + "You: " + Style.RESET_ALL)
            
            if user_input.lower() in ["exit", "quit", "menu"]:
                print(Fore.YELLOW + "Returning to menu...")
                break
            
            if not user_input.strip():
                continue

            print(Fore.MAGENTA + f"{config.app_name}: " + Style.RESET_ALL, end="", flush=True)
            
            if streaming:
                async for token in chat_service.stream_chat_completion(
                    user_input, 
                    system_prompt=system_prompt, 
                    thread_id=thread_id
                ):
                    print(token, end="", flush=True)
                print("\n")
            else:
                response = await chat_service.chat_completion(
                    user_input, 
                    system_prompt=system_prompt, 
                    thread_id=thread_id
                )
                print(response + "\n")

        except Exception as e:
            print(Fore.RED + f"\nError in async session: {e}")
            break
