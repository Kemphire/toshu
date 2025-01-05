import typer
from database.db import SessionLocal
from database.models import Priority, Task, Category
from rich import print
from rich.console import Console
from typing import Optional
from typing_extensions import Annotated
from rich.prompt import Prompt

from .helpers import *

app = typer.Typer()

console = Console()


@app.command(short_help="to add task")
def add_task(
    categ: Annotated[
        str,
        typer.Option(
            help="Category of your task",
        ),
    ],
    description: str = typer.Option(None),
    title: Annotated[Optional[str], typer.Argument(help="Title of your task")] = None,
    priority: Annotated[
        Priority,
        typer.Option(
            help="Priority of your task",
            show_choices=True,
            case_sensitive=False,
        ),
    ] = Priority.L,
    interactive: bool = False,
):
    if not interactive:
        if not title:
            title = typer.prompt("Enter title")
        with SessionLocal() as session:
            try:
                category = find_category(session, categ)
                new_task = Task(
                    title=title,
                    description=description,
                    category_id=category.id,
                    priority=priority,
                )
                session.add(new_task)
                console.print(
                    f"Task with title [red]{title}[/] in category [yello]{categ}[/] create [green]succesfully[/] :beer_mug:",
                    style="conceal",
                )
                session.commit()
            except Exception as e:
                print(e)
    else:
        interactive_add_task_int(categ, console)


@app.command(short_help="Mark task as completed")
def mark_updated(
    tit_o_id: Annotated[
        str,
        typer.Argument(
            help="Provid either ID or title of task",
        ),
    ],
):
    """Mark the task as updated for based on the id or title of the task"""
    completed = True
    with SessionLocal() as session:
        if tit_o_id.isdigit():
            task = session.get(Task, int(tit_o_id))
            if not task:
                print(f"There is no task with id {tit_o_id}")
                raise typer.Exit()
            completed = task.completed
        else:
            task = session.query(Task).filter(Task.title == tit_o_id)
            if not task:
                panic("There is not task with title {tit_o_id}")
            choices = [str(ta.id) for ta in task]
            if task.count() > 1:
                id_to_update = Prompt.ask(
                    "There are more than one task of same title, Enter the id of the task to delete",
                    choices=choices,
                )
                task = session.get(Task, int(id_to_update))
            else:
                task = task.first()
            completed = task.completed
        if not completed:
            task.completed = True
        else:
            panic("Task is already completed :poop:")
        session.commit()
        print(
            f"Task with title [bold green]{task.title}[/] marked as completed :beer_mug:"
        )


@app.command()
def update_task(id: int):
    """Update the task based on given id of task"""
    with SessionLocal() as session:
        task = session.get(Task, id)
        if not task:
            print(f"[bold red]Session with [blue]{id}[/blue] not present[/bold red]")
            raise typer.Exit()
        old_title, old_completed_status, old_category = (
            task.title,
            task.completed,
            task.category,
        )

        # ask about the fields which user wants to modify
        update_title = typer.confirm("Do you want to update the title?", default=False)
        update_description = typer.confirm(
            "Do you want to update the description?", default=False
        )
        if task.completed:
            update_completed = typer.confirm(
                "Do you want to mark the status as not-completed", default=False
            )
            if update_completed:
                task.completed = False
        else:
            update_completed = typer.confirm(
                "Do you want to mark the status as completed", default=False
            )
            if update_completed:
                mark_updated(str(id))
        category_change = typer.confirm("Do you want to change your category?")
        if category_change:
            categories = session.query(Category).filter(Category.id != task.category_id)
            # only the value of choices array will be considered, valid input for new_categ prompt
            choices = [str(cat.name) for cat in categories]
            new_categ = Prompt.ask(
                "Choose from the avialable categories", choices=choices
            )
            task.category = categories[choices.index(new_categ)]
            task.category_id = categories[choices.index(new_categ)].id

        if update_title:
            new_title = typer.prompt("Enter the new title", default=task.title)
            task.title = new_title
        if update_description:
            new_description = typer.prompt(
                "Enter the new description", default=task.description
            )
            task.description = new_description

        if not (update_title | update_completed | update_description | category_change):
            print("[bold green]No changes have been made[/bold green]")
        else:
            print(f"Task with title [bold red]{old_title}[/bold red] has been changed!")

        session.commit()


@app.command(short_help="get id by title")
def get_id(title: str):
    with SessionLocal() as session:
        task = session.query(Task).filter(Task.title == title)[0]
        if task is None:
            panic(f"No task with {title} exists.")
        print(task.id)
        session.commit()
