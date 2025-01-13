from time import sleep
from typing import List

import typer
from rich import print
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table

from database.db import SessionLocal
from database.models import Category

from ..helpers import *

app = typer.Typer()

console = Console()


@app.command(short_help="list all categories", name="list")
@handle_pipes
def list_category():
    """
    List all the category, with all the related attributes
    """
    spinner = Spinner("bouncingBall", text="Fetching categories...")

    with Live(spinner, refresh_per_second=10, console=console) as live:
        with SessionLocal() as session:
            cats: List[Category] = session.query(Category).all()
        for _ in range(10):
            sleep(0.1)
            live.refresh()
    if not cats:
        print(
            "[red]No Category[/]\nAdd it by running [bold green]add-category[/] [blue]cat_name[/]"
        )
    else:
        table = Table(header_style="bold cyan")
        table.add_column("#", style="dim", width=1)
        table.add_column("Name", justify="center")
        table.add_column("Total Task")
        for cat in cats:
            table.add_row(
                str(cat.id), f"[green]{cat.name}[/]", f"[blue]{cat.no_of_tasks}[/]"
            )
        console.print(table)
