from typing import Optional

import typer
from rich import print
from rich.console import Console
from rich.prompt import Confirm, Prompt
from typing_extensions import Annotated

from database.db import SessionLocal
from database.models import Priority, Task

from .helpers import *

app = typer.Typer()

console = Console()


@app.command(short_help="to add task")
def add(
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
    due: Annotated[str | None, typer.Option(help="add a deadline")] = None,
):
    if not interactive:
        if not title:
            title = typer.prompt("Enter title")
        with SessionLocal() as session:
            if due:
                due_datetime = return_datetime(due)
                if due_datetime is None:
                    panic(f"Your passed due date [red]{due}[/] cannot be intrpreted")
                elif due_datetime < datetime.now():
                    panic(
                        f"Your passed time, i.e. [red]{due}[/] whose interpretation is [blue]{due_datetime}[/] is in past, only future dates are allowed"
                    )
            try:
                category = find_category(session, categ)
                task_attribute = {
                    "title": title,
                    "description": description,
                    "category_id": category.id,
                    "priority": priority,
                }
                if due:
                    task_attribute["due"] = due_datetime
                new_task = Task(**task_attribute)
                session.add(new_task)
                console.print(
                    f"Task with title [red]{title}[/] in category [yello]{categ}[/] created [green]succesfully[/] :beer_mug:",
                    style="conceal",
                )
                session.commit()
            except Exception as e:
                print(e)
    else:
        interactive_add_task_int(categ, console)


@app.command(short_help="Mark task as completed")
def complete(
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
            if task.count() == 0:
                panic(f"There is not task with title [blue]{tit_o_id}[/]")
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


# @app.command()
# def update_task(id: int):
#     """Update the task based on given id of task"""
#     with SessionLocal() as session:
#         task = session.get(Task, id)
#         if not task:
#             print(f"[bold red]Session with [blue]{id}[/blue] not present[/bold red]")
#             raise typer.Exit()
#         old_title, old_completed_status, old_category = (
#             task.title,
#             task.completed,
#             task.category,
#         )
#
#         # ask about the fields which user wants to modify
#         update_title = typer.confirm("Do you want to update the title?", default=False)
#         update_description = typer.confirm(
#             "Do you want to update the description?", default=False
#         )
#         if task.completed:
#             update_completed = typer.confirm(
#                 "Do you want to mark the status as not-completed", default=False
#             )
#             if update_completed:
#                 task.completed = False
#         else:
#             update_completed = typer.confirm(
#                 "Do you want to mark the status as completed", default=False
#             )
#             if update_completed:
#                 mark_updated(str(id))
#         category_change = typer.confirm("Do you want to change your category?")
#         if category_change:
#             categories = session.query(Category).filter(Category.id != task.category_id)
#             # only the value of choices array will be considered, valid input for new_categ prompt
#             choices = [str(cat.name) for cat in categories]
#             new_categ = Prompt.ask(
#                 "Choose from the avialable categories", choices=choices
#             )
#             task.category = categories[choices.index(new_categ)]
#             task.category_id = categories[choices.index(new_categ)].id
#
#         if update_title:
#             new_title = typer.prompt("Enter the new title", default=task.title)
#             task.title = new_title
#         if update_description:
#             new_description = typer.prompt(
#                 "Enter the new description", default=task.description
#             )
#             task.description = new_description
#
#         if not (update_title | update_completed | update_description | category_change):
#             print("[bold green]No changes have been made[/bold green]")
#         else:
#             print(f"Task with title [bold red]{old_title}[/bold red] has been changed!")
#
#         session.commit()


@app.command(short_help="get id by title")
def get_id(title: str):
    with SessionLocal() as session:
        task = session.query(Task).filter(Task.title == title)[0]
        if task is None:
            panic(f"No task with {title} exists.")
        print(task.id)
        session.commit()


@app.command()
def update_task(title_or_id: str):
    """Update the task based on given id/title of task"""
    with SessionLocal() as session:
        task_query = session.query(Task).filter(
            Task.id == int(title_or_id)
            if title_or_id.isdigit()
            else Task.title == title_or_id
        )

        if (tasks_found := task_query.count()) == 0:
            panic(f"There are no task with id/title {title_or_id}!")

        if tasks_found > 1:
            choices = [str(task.id) for task in task_query]

            task_id = Prompt.ask(
                f"There are more than one task with id {title_or_id}, please select from the avialable choices",
                choices=choices,
                default=choices[0],
            )

            task: Task = task_query.get(int(task_id))
        else:
            task: Task = task_query.first()

        def update_field(
            field_name: str,
            prompt_text: str,
            choices: List[str] | Any = None,
            default=None,
        ) -> str | None:
            if Confirm.ask(f"Do you want to update the {field_name}?", default=False):
                return Prompt.ask(prompt_text, choices=choices, default=default)
            return None

        update_dict = {}
        if new_title := update_field(
            "title",
            f"Do you really want to update update your title from [blue]{task.title}[/] to something else?",
            default=task.title,
        ):
            update_dict["title"] = new_title

        if new_description := update_field(
            "description",
            f"Do you want your task [blue]{task.title}'s[/] description?",
            default=task.description,
        ):
            update_dict["description"] = new_description

        if new_completion := bool(
            update_field(
                "completion status",
                f"Do you want to change the completion status from [red]{task.completed}[/] to [blue]{not task.completed}[/]?",
                default=False,
                choices=[str(False), str(True)],
            )
        ):
            update_dict["completed"] = new_completion

        if new_priority := update_field(
            "priority",
            f"Do you want to change to change the priority from [blue]{task.priority}[/] to something else?",
            choices=[Priority.L, Priority.M, Priority.T],
            default=task.priority,
        ):
            update_dict["priority"] = new_priority

        if not update_dict:
            panic(f"Nothing changed so far for [blue]{task}[/]")
        else:
            for key, value in update_dict.items():
                setattr(task, key, value)
                print(f"New {key} ---> {value}")
            session.commit()
