from datetime import datetime
from typing import Annotated, Optional

import typer
from rich import print
from sqlalchemy.orm import joinedload

from database.db import SessionLocal
from database.models import Category, Priority, Task

from .helpers import get_category_names_from_database, panic, print_colorful_table

app = typer.Typer()


def callback_for_category_check(ctx: typer.Context, value: str):
    if ctx.resilient_parsing:
        return
    if value is None:
        return
    if value in get_category_names_from_database():
        return value
    else:
        raise typer.BadParameter(
            f"{value} is not a valid name of any of the available category"
        )


def callback_for_title_check(ctx: typer.Context, value: str):
    if ctx.resilient_parsing:
        return
    if value is None:
        return
    with SessionLocal() as session:
        if value in [task.title for task in session.query(Task).all()]:
            return value
        else:
            raise typer.BadParameter(f"{value} in not a title for any of the task")


def callback_for_date_scruitiny(ctx: typer.Context, value: datetime):
    if ctx.resilient_parsing:
        return
    if value is None:
        return
    if value < datetime.now():
        return value
    else:
        raise typer.BadParameter(f"{value}: forward dates are not allowed")


@app.command(
    short_help="filter tasks based on parameters, based on logical Intersection"
)
def filter(
    completed: Annotated[bool, typer.Option(help="task completion status")] = None,
    task_title: Annotated[
        Optional[str],
        typer.Option("-t", "--task-title", callback=callback_for_title_check),
    ] = None,
    categ: Annotated[
        Optional[str],
        typer.Option(
            "-c",
            "--category",
            help="None for orphan",
            callback=callback_for_category_check,
        ),
    ] = None,
    created_after: Annotated[
        Optional[datetime],
        typer.Option(
            "-c-before",
            "--created-before",
            help="task created after this datetime",
            formats=[
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%m/%d/%Y",
                "%m/%d/%Y %H:%M:%S",
            ],
            callback=callback_for_date_scruitiny,
        ),
    ] = None,
    priority: Annotated[
        Optional[Priority], typer.Option("-p", "--priority", show_choices=True)
    ] = None,
):
    """
    filter task, execute a sql where
    """
    # not correct currently try to use sql where statement using sqlalchemy, it will be much better than finding all of the filter seperately
    # and then combining and converting them into set

    with SessionLocal() as session:
        filters = []
        if task_title:
            filters.append(Task.title.like(f"%{task_title}%"))
        if created_after:
            filters.append(Task.created_at >= created_after)
        if priority:
            filters.append(Task.priority == priority)
        if completed is not None:
            filters.append(Task.completed == completed)

        query = session.query(Task).options(joinedload(Task.category))

        if categ:
            query = query.join(Category).filter(
                Task.category.has(Category.name == categ)
            )

        if filters:
            query = query.filter(*filters)

        matching_task = query.all()

        if (len_matching_task := len(matching_task)) == 0:
            panic("There are zero matching tasks for this filters provided")

        print(f"There are {len_matching_task} satisfying this filter")

        tablular_dict = {
            "Title": [task.title for task in matching_task],
            "Description": [task.description for task in matching_task],
            "Category": [task.category for task in matching_task],
            "Created at (date)": [task.created_at.date() for task in matching_task],
            "Creaated at (time)": [
                str(task.created_at.time()).split(".")[0] for task in matching_task
            ],
            "Priority": [task.priority for task in matching_task],
            "Completed": [
                ":white_check_mark:" if bool(task.completed) else ":x:"
                for task in matching_task
            ],
        }

        print_colorful_table(tablular_dict)
