from colorama import init, Fore
import sys
from cli.ui import show_menu, print_header
from cli.chat_handler import start_chat
from cli.utils import check_system_health
from core.config import config

# Initialize colorama
init(autoreset=True)

def main():
    """
    Entry point for the CLI. Handles the main menu loop.
    """
    first_run = True
    
    while True:
        try:
            if first_run:
                # print_header() # Removed at startup as it's repetitive
                first_run = False
            
            # Show navigation menu
            choice = show_menu()
            
            if choice == "1":
                # Start chat with streaming
                start_chat(streaming=True)
            elif choice == "2":
                # Start chat without streaming
                start_chat(streaming=False)
            elif choice.lower() == "h":
                # Check system health
                check_system_health()
            elif choice == "0" or choice.lower() == "exit":
                print(Fore.YELLOW + "\nGoodbye! Have a great day.")
                sys.exit(0)
            else:
                print(Fore.RED + "\nInvalid selection. Please try again.")
        
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nExiting CLI...")
            break
        except Exception as e:
            print(Fore.RED + f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
