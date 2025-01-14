from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({"info": "bold green", "mid": "bold cyan", "bad": "bold red"})
CONSOLE = Console(theme=custom_theme)
