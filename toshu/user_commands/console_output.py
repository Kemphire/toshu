from time import sleep
from typing import List

import typer
from rich import print
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table

from database.db import SessionLocal
from database.models import Category, Task

from .helpers import *

app = typer.Typer()

console = Console()


def list_category_int(to_highlight: str, console: Console):
    with SessionLocal() as session:
        cats: List[Category] = session.query(Category).all()
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
            if cat.name != to_highlight:
                table.add_row(
                    str(cat.id), f"[green]{cat.name}[/]", f"[blue]{cat.no_of_tasks}[/]"
                )
            else:
                table.add_row(
                    str(cat.id),
                    f"[green]{cat.name}[/]",
                    f"[blue]{cat.no_of_tasks}[/]",
                    style="magenta on yellow",
                )

        console.print(table)


@app.command(short_help="Display list of task, with related data", name="list")
@handle_pipes
def show_list():
    """
    Show the list of avaialbe tasks
    """
    spinner = Spinner("bouncingBall", text="Fetching tasks...")
    with Live(spinner, refresh_per_second=10, console=console) as live:
        for _ in range(5):
            sleep(0.05)  # Small sleep intervals
            live.refresh()  # Force spinner update
    with SessionLocal() as session:
        tasks = session.query(Task).all()
        session.commit()
        if not tasks:
            print("[red]No task[/]")
        else:
            not_completed = count_not_completed(tasks)
            if not_completed > 0:
                table = Table(
                    show_header=True,
                    header_style="bold magenta",
                    caption=f"You have [bold red]{not_completed}[/] tasks not completed",
                    padding=(0, 3),
                )
            else:
                table = Table(
                    show_header=True,
                    header_style="bold magenta",
                    caption="You have completed all your task",
                    padding=(0, 3),
                )

            table.add_column(
                "ID",
                style="dim",
            )
            table.add_column(
                "Title",
                justify="center",
            )
            table.add_column("Description", justify="right")
            table.add_column("Category")
            table.add_column("Priority")
            table.add_column("Created At (date)", justify="center")
            table.add_column("Created At (time)", justify="center")
            table.add_column("Completed")
            for task in tasks:
                row_content = [
                    str(task.id),
                    f"[green]{task.title}[/]",
                    f"[blue]{task.description}[/]",
                ]
                if task.category:
                    row_content.extend(
                        [
                            f"[yellow]{task.category.name}[/]",
                        ]
                    )
                else:
                    row_content.extend([f"[yellow]{None}[/]"])
                row_content.extend(
                    [
                        f"[cyan]{task.priority}[/]",
                        f"{str(task.created_at.date())}",
                        f"{str(task.created_at.time()).split('.')[0]}",
                    ]
                )
                if bool(task.completed):
                    row_content.append(":white_check_mark:")
                    table.add_row(*row_content, style="green")
                else:
                    row_content.append(":x:")
                    table.add_row(*row_content, style="red")
            console.print(table)

        #     dict_obj = {
        #         "ID": [str(task.id) for task in tasks],
        #         "Title": [task.title for task in tasks],
        #         "Description": [task.description for task in tasks],
        #         "Category": [
        #             task.category.name for task in tasks if task.category is not None
        #         ],
        #         "Priority": [task.priority for task in tasks],
        #         "Completed": [
        #             ":white_check_mark:" if bool(task.completed) else ":x:"
        #             for task in tasks
        #         ],
        #     }
        # return dict_obj
