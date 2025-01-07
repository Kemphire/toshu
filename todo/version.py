import typer
from rich import print

app = typer.Typer()

VERSION = 0.01


@app.command(short_help="Show version, and exit")
def version():
    print(f"Version [bold red]{VERSION}[/]")
