import json
import sys

from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text


console = Console()
USER_PROMPT = "You: "
USER_STYLE = "bold bright_cyan"


def _thinking_panel(thinking: str) -> Panel:
    return Panel(
        Markdown(thinking, style="dim italic"),
        title="[bold bright_magenta]Thinking[/bold bright_magenta]",
        border_style="bright_magenta",
        padding=(0, 1),
    )


def prompt_user_message() -> str:
    console.print()
    if sys.stdin.isatty():
        return console.input(Text(USER_PROMPT, style=USER_STYLE))

    message = input()
    display_user_message(message)
    return message


def display_user_message(message: str) -> None:
    console.print(Text.assemble((USER_PROMPT, USER_STYLE), message))


def display_assistant_message(message: str) -> None:
    console.print()
    console.print(Text("Assistant", style="bold bright_green"))
    console.print(Markdown(message))


def display_thinking(thinking: str) -> None:
    console.print()
    console.print(_thinking_panel(thinking))


class StreamingChatDisplay:
    def __init__(self) -> None:
        self.thinking = ""
        self.message = ""
        self._live = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._live:
            self._live.stop()

    def add_thinking(self, text: str) -> None:
        self.thinking += text
        self._update()

    def add_message(self, text: str) -> None:
        self.message += text
        self._update()

    def _update(self) -> None:
        if not self._live:
            console.print()
            self._live = Live(
                self._render(),
                console=console,
                refresh_per_second=12,
            )
            self._live.start()
            return

        self._live.update(self._render(), refresh=False)

    def _render(self) -> Group:
        sections = []
        if self.thinking:
            sections.append(_thinking_panel(self.thinking))
        if self.message:
            if sections:
                sections.append(Text())
            sections.extend([
                Text("Assistant", style="bold bright_green"),
                Markdown(self.message),
            ])
        return Group(*sections)


def display_tool_call(name: str, arguments: str) -> None:
    try:
        formatted_arguments = json.dumps(json.loads(arguments), indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        formatted_arguments = arguments

    console.print()
    console.print(Text(f"Tool call: {name}", style="bold yellow"))
    console.print(Syntax(formatted_arguments, "json", word_wrap=True, background_color="default"))


def display_error(message: str) -> None:
    console.print(Text.assemble(("Error: ", "bold bright_red"), message))
