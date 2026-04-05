"""
chat_handler.py — Nura's Rich CLI interface

Run with:
  python cli_run.py
  python main.py cli

Commands inside the CLI:
  /help     show commands
  /memory   show what Nura remembers about you
  /history  show this session's messages
  /new      start a fresh session
  /clear    clear the screen
  /exit     quit
"""
import asyncio
import uuid
from datetime import datetime

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text

from agents.orchestrator import nura
from core.config import config
from utils.logger import get_logger

logger = get_logger("cli")
console = Console()

# ── Styling ───────────────────────────────────────────────────────────────────

PROMPT_STYLE = Style.from_dict({
    "prompt": "bold #7c3aed",
})

AGENT_EMOJI = {
    "chat":          "💬",
    "reasoning":     "🧠",
    "entertainment": "🎉",
    "realtime":      "🌐",
    "system":        "⚙️",
    "knowledge":     "📚",
    "mcp":           "🔗",
}

AGENT_COLOR = {
    "chat_agent":          "bold cyan",
    "reasoning_agent":     "bold blue",
    "entertainment_agent": "bold yellow",
    "realtime_agent":      "bold green",
    "system_agent":        "bold red",
    "knowledge_agent":     "bold magenta",
    "mcp_agent":           "bold orange3",
}


class NuraCLI:

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.history: list[dict] = []     # kept in-memory for multi-turn context
        self.prompt_session = PromptSession(
            history=FileHistory(".nura_history"),
            auto_suggest=AutoSuggestFromHistory(),
        )

    # ── Welcome ───────────────────────────────────────────────────────────────

    def _welcome(self):
        hour = datetime.now().hour
        greeting = (
            "Good morning" if hour < 12
            else "Good afternoon" if hour < 17
            else "Good evening"
        )
        console.print()
        console.print(Panel(
            f"[bold #7c3aed]Nura[/bold #7c3aed]  [dim]your personal AI assistant[/dim]\n\n"
            f"[dim]{greeting}, {config.user_name}.[/dim]   "
            f"[dim]Session: {self.session_id[:8]}[/dim]\n\n"
            "[dim]Type anything to start. Commands: "
            "[bold]/help[/bold]  [bold]/memory[/bold]  "
            "[bold]/history[/bold]  [bold]/new[/bold]  [bold]/exit[/bold][/dim]",
            border_style="#7c3aed",
            padding=(0, 2),
        ))
        console.print()

    # ── Response rendering ────────────────────────────────────────────────────

    def _print_response(self, response: str, intent: str, agent: str):
        emoji = AGENT_EMOJI.get(intent, "✨")
        color = AGENT_COLOR.get(agent, "bold white")
        title = f"[{color}]{emoji} Nura[/{color}]  [dim]{agent}[/dim]"

        # Render as Markdown if it contains markdown syntax
        has_md = any(s in response for s in ["**", "```", "##", "\n- ", "\n* "])
        content = Markdown(response) if has_md else Text(response)

        console.print()
        console.print(Panel(content, title=title, border_style="dim", padding=(0, 1)))
        console.print()

    # ── Commands ──────────────────────────────────────────────────────────────

    async def _handle_command(self, cmd: str) -> bool:
        """Returns True if it was a slash command — don't pass to Nura."""
        c = cmd.strip().lower()

        if c in ("/exit", "/quit", "/bye"):
            console.print(
                "\n[bold #7c3aed]Nura:[/bold #7c3aed] [dim]Bye, "
                f"{config.user_name}! 👋[/dim]\n"
            )
            raise SystemExit(0)

        elif c == "/help":
            console.print(Panel(
                "[bold]Commands[/bold]\n\n"
                "  [cyan]/help[/cyan]      show this\n"
                "  [cyan]/memory[/cyan]    show what Nura remembers about you\n"
                "  [cyan]/history[/cyan]   show this session's messages\n"
                "  [cyan]/new[/cyan]       start a fresh session\n"
                "  [cyan]/clear[/cyan]     clear the screen\n"
                "  [cyan]/exit[/cyan]      quit\n\n"
                "[bold]Tips[/bold]\n"
                "  Say [italic]'Remember that...'[/italic] to store something\n"
                "  Speak Hindi, English, or Hinglish — Nura adapts",
                title="[bold]Nura Help[/bold]",
                border_style="dim",
            ))
            return True

        elif c == "/clear":
            console.clear()
            self._welcome()
            return True

        elif c == "/new":
            self.session_id = str(uuid.uuid4())
            self.history = []
            console.print(f"\n[dim]New session: {self.session_id[:8]}[/dim]\n")
            return True

        elif c == "/history":
            if not self.history:
                console.print("\n[dim]No messages in this session yet.[/dim]\n")
            else:
                console.print()
                for turn in self.history:
                    label = (
                        "[bold cyan]You[/bold cyan]"
                        if turn["role"] == "user"
                        else "[bold #7c3aed]Nura[/bold #7c3aed]"
                    )
                    console.print(f"{label}: {turn['content'][:200]}")
                console.print()
            return True

        elif c == "/memory":
            await self._show_memory()
            return True

        return False

    async def _show_memory(self):
        from core.knowledge.mongo_store import mongo_store
        items = await mongo_store.get_all_knowledge(limit=20)
        if not items:
            console.print("\n[dim]No memories yet. Start talking to Nura![/dim]\n")
            return
        rows = "\n".join(
            f"  [dim][{item.get('category', 'fact')}][/dim]  {item['content'][:100]}"
            for item in items
        )
        console.print()
        console.print(Panel(
            rows,
            title="[bold magenta]📚 What Nura remembers about you[/bold magenta]",
            border_style="magenta",
        ))
        console.print()

    # ── Main loop ─────────────────────────────────────────────────────────────

    async def run(self):
        self._welcome()

        while True:
            # Get input from user
            try:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.prompt_session.prompt(
                        [("class:prompt", "You ❯ ")],
                        style=PROMPT_STYLE,
                    ),
                )
            except (KeyboardInterrupt, EOFError):
                console.print("\n[dim]Use /exit to quit.[/dim]\n")
                continue

            user_input = user_input.strip()
            if not user_input:
                continue

            # Slash commands
            if user_input.startswith("/"):
                await self._handle_command(user_input)
                continue

            # Show spinner while Nura thinks
            result = None
            with Live(
                Spinner("dots", text="[dim]✨ Thinking...[/dim]"),
                console=console,
                refresh_per_second=10,
                transient=True,
            ):
                try:
                    result = await nura.chat(
                        message=user_input,
                        session_id=self.session_id,
                        history=self.history,
                    )
                except Exception as e:
                    logger.error("Chat error", error=str(e))
                    result = {
                        "response": f"Kuch issue aa gaya: {e}",
                        "intent": "chat",
                        "agent": "chat_agent",
                        "session_id": self.session_id,
                        "error": str(e),
                    }

            # Update in-memory history for multi-turn context
            self.history.append({"role": "user",      "content": user_input})
            self.history.append({"role": "assistant",  "content": result["response"]})

            # Cap history at 20 turns (40 messages)
            if len(self.history) > 40:
                self.history = self.history[-40:]

            self._print_response(
                response=result["response"],
                intent=result.get("intent", "chat"),
                agent=result.get("agent", "chat_agent"),
            )


# ── Entry point ───────────────────────────────────────────────────────────────

async def run_cli():
    await nura.init()
    cli = NuraCLI()
    await cli.run()
