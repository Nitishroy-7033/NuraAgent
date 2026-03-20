from colorama import Fore, Style
from core.config import config

def print_header():
    print(Fore.CYAN + Style.BRIGHT + "="*50)
    print(Fore.CYAN + Style.BRIGHT + f"{' '*13}NuraAgent CLI - {config.app_name}")
    print(Fore.CYAN + Style.BRIGHT + "="*50)

def show_menu():
    print(Fore.CYAN + "\nSelect an option:")
    print(f"  {Fore.GREEN}1. {Fore.WHITE}Stream Chat (Real-time)")
    print(f"  {Fore.GREEN}2. {Fore.WHITE}Normal Chat (Full response)")
    print(f"  {Fore.YELLOW}H. {Fore.WHITE}System Health")
    print(f"  {Fore.RED}0. {Fore.WHITE}Exit")
    return input(Fore.MAGENTA + "\nChoice > " + Style.RESET_ALL)

def clear_line():
    print("\r" + " " * 80 + "\r", end="", flush=True)
