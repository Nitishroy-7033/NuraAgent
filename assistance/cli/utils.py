import requests
from colorama import Fore, Style
from core.config import config

def check_system_health():
    """
    Checks the status of the Ollama server.
    """
    print(Fore.CYAN + "\nSystem Health Check" + "-"*30)
    try:
        response = requests.get(f"{config.ollama_base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            print(Fore.GREEN + f"Status: Ollama IS RUNNING at {config.ollama_base_url}")
            models = response.json().get("models", [])
            print(f"Available models: {[m['name'] for m in models]}")
        else:
            print(Fore.RED + f"Status: Ollama returned status code {response.status_code}")
    except Exception as e:
        print(Fore.RED + f"Status: ERROR (Cannot connect to Ollama): {e}")
    print("-" * 30 + "\n")
    input("Press Enter to continue...")
