from pathlib import Path

import toml
import typer
from rich import print

app = typer.Typer()

pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"

with pyproject_path.open() as project_config_file:
    config = toml.load(project_config_file)
    VERSION = config["project"]["version"]


@app.command(short_help="Show version, and exit")
def version():
    print(f"Version [bold red]{VERSION}[/]")
